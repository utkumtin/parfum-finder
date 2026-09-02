#define UNICODE
#define _UNICODE

#include <windows.h>
#include <shellapi.h>
#include <stdio.h>
#include <stdlib.h>
#include <wchar.h>

enum {
    parent_wait_timeout_ms = 60000,
};

typedef struct {
    DWORD parent_pid;
    const wchar_t *installer;
    const wchar_t *ready_event;
    const wchar_t *log_path;
    const wchar_t *setup_log_path;
} arguments_t;

static void append_log(const wchar_t *log_path, const wchar_t *message) {
    FILE *file = NULL;
    SYSTEMTIME now;

    GetLocalTime(&now);
    if (_wfopen_s(&file, log_path, L"a, ccs=UTF-8") != 0 || file == NULL) {
        return;
    }
    fwprintf(
        file,
        L"%04u-%02u-%02u %02u:%02u:%02u %ls\n",
        now.wYear,
        now.wMonth,
        now.wDay,
        now.wHour,
        now.wMinute,
        now.wSecond,
        message
    );
    fclose(file);
}

static const wchar_t *argument_value(
    int argc, wchar_t **argv, const wchar_t *name
) {
    int index;

    for (index = 1; index + 1 < argc; index++) {
        if (wcscmp(argv[index], name) == 0) {
            return argv[index + 1];
        }
    }
    return NULL;
}

static BOOL parse_arguments(int argc, wchar_t **argv, arguments_t *arguments) {
    const wchar_t *pid_text = argument_value(argc, argv, L"--parent-pid");
    wchar_t *end = NULL;
    unsigned long parsed_pid;

    if (pid_text == NULL) {
        return FALSE;
    }
    parsed_pid = wcstoul(pid_text, &end, 10);
    if (*pid_text == L'\0' || *end != L'\0' || parsed_pid == 0 || parsed_pid > MAXDWORD) {
        return FALSE;
    }
    arguments->parent_pid = (DWORD)parsed_pid;
    arguments->installer = argument_value(argc, argv, L"--installer");
    arguments->ready_event = argument_value(argc, argv, L"--ready-event");
    arguments->log_path = argument_value(argc, argv, L"--log");
    arguments->setup_log_path = argument_value(argc, argv, L"--setup-log");
    return arguments->installer != NULL && arguments->ready_event != NULL &&
        arguments->log_path != NULL && arguments->setup_log_path != NULL;
}

static wchar_t *setup_parameters(const wchar_t *setup_log_path) {
    const wchar_t *prefix = L"/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /LOG=\"";
    size_t capacity = wcslen(prefix) + wcslen(setup_log_path) + 3;
    wchar_t *parameters = calloc(capacity, sizeof(*parameters));

    if (parameters != NULL) {
        _snwprintf_s(parameters, capacity, _TRUNCATE, L"%ls%ls\"", prefix, setup_log_path);
    }
    return parameters;
}

static DWORD launch_setup(
    const wchar_t *installer, const wchar_t *parameters, const wchar_t *log_path
) {
    SHELLEXECUTEINFOW execution = {0};
    DWORD error;
    DWORD exit_code;
    DWORD wait_result;

    execution.cbSize = sizeof(execution);
    execution.fMask = SEE_MASK_NOCLOSEPROCESS;
    execution.lpVerb = L"open";
    execution.lpFile = installer;
    execution.lpParameters = parameters;
    execution.nShow = SW_SHOWNORMAL;
    if (!ShellExecuteExW(&execution)) {
        error = GetLastError();
        if (error != ERROR_ELEVATION_REQUIRED) {
            if (error == ERROR_CANCELLED) {
                append_log(log_path, L"handoff cancelled: UAC consent was declined");
            } else {
                wchar_t message[96];
                _snwprintf_s(
                    message, _countof(message), _TRUNCATE,
                    L"handoff error: installer launch failed (%lu)", error
                );
                append_log(log_path, message);
            }
            return error;
        }
        execution.lpVerb = L"runas";
        if (!ShellExecuteExW(&execution)) {
            error = GetLastError();
            if (error == ERROR_CANCELLED) {
                append_log(log_path, L"handoff cancelled: UAC consent was declined");
            } else {
                wchar_t message[96];
                _snwprintf_s(
                    message, _countof(message), _TRUNCATE,
                    L"handoff error: elevated installer launch failed (%lu)", error
                );
                append_log(log_path, message);
            }
            return error;
        }
    }
    if (execution.hProcess == NULL) {
        append_log(log_path, L"handoff error: installer process handle was unavailable");
        return ERROR_INVALID_HANDLE;
    }
    wait_result = WaitForSingleObject(execution.hProcess, INFINITE);
    if (wait_result != WAIT_OBJECT_0 || !GetExitCodeProcess(execution.hProcess, &exit_code)) {
        error = GetLastError();
        CloseHandle(execution.hProcess);
        append_log(log_path, L"handoff error: installer exit code could not be read");
        return error == ERROR_SUCCESS ? ERROR_GEN_FAILURE : error;
    }
    CloseHandle(execution.hProcess);
    if (exit_code != 0) {
        wchar_t message[96];
        _snwprintf_s(
            message, _countof(message), _TRUNCATE,
            L"handoff error: installer exit code %lu", exit_code
        );
        append_log(log_path, message);
        return exit_code;
    }
    append_log(log_path, L"handoff complete: installer exited successfully");
    return ERROR_SUCCESS;
}

int WINAPI wWinMain(HINSTANCE instance, HINSTANCE previous, PWSTR command_line, int show) {
    int argc = 0;
    wchar_t **argv = CommandLineToArgvW(GetCommandLineW(), &argc);
    arguments_t arguments = {0};
    HANDLE ready_event;
    HANDLE parent;
    DWORD parent_error;
    DWORD wait_result;
    DWORD result;
    wchar_t *parameters;

    (void)instance;
    (void)previous;
    (void)command_line;
    (void)show;
    if (argv == NULL || !parse_arguments(argc, argv, &arguments)) {
        if (argv != NULL) {
            LocalFree(argv);
        }
        return ERROR_INVALID_PARAMETER;
    }

    append_log(arguments.log_path, L"handoff started");
    ready_event = OpenEventW(EVENT_MODIFY_STATE, FALSE, arguments.ready_event);
    if (ready_event == NULL || !SetEvent(ready_event)) {
        append_log(arguments.log_path, L"handoff error: ready event could not be signalled");
        if (ready_event != NULL) {
            CloseHandle(ready_event);
        }
        LocalFree(argv);
        return ERROR_INVALID_HANDLE;
    }
    CloseHandle(ready_event);
    append_log(arguments.log_path, L"handoff ready");

    parent = OpenProcess(SYNCHRONIZE, FALSE, arguments.parent_pid);
    if (parent == NULL) {
        parent_error = GetLastError();
        if (parent_error == ERROR_INVALID_PARAMETER) {
            append_log(arguments.log_path, L"handoff parent already exited");
        } else {
            wchar_t message[96];
            _snwprintf_s(
                message, _countof(message), _TRUNCATE,
                L"handoff error: parent process could not be opened (%lu)", parent_error
            );
            append_log(arguments.log_path, message);
            LocalFree(argv);
            return parent_error;
        }
    } else {
        wait_result = WaitForSingleObject(parent, parent_wait_timeout_ms);
        CloseHandle(parent);
        if (wait_result != WAIT_OBJECT_0) {
            append_log(arguments.log_path, L"handoff error: app did not exit in time");
            LocalFree(argv);
            return wait_result == WAIT_TIMEOUT ? WAIT_TIMEOUT : ERROR_GEN_FAILURE;
        }
    }

    parameters = setup_parameters(arguments.setup_log_path);
    if (parameters == NULL) {
        append_log(arguments.log_path, L"handoff error: installer parameters could not be allocated");
        LocalFree(argv);
        return ERROR_NOT_ENOUGH_MEMORY;
    }
    result = launch_setup(arguments.installer, parameters, arguments.log_path);
    free(parameters);
    LocalFree(argv);
    return (int)result;
}
