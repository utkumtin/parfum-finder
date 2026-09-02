---
type: "query"
date: "2026-09-02T18:03:13.560836+00:00"
question: "In the Windows application, when I release a new version, I click the ‘Update’ button to install the update, and the new update is downloaded. However, the application then closes and the installer does not launch. By pressing Win + R and then running the downloaded installer from the ‘%temp%’ directory, I am able to install the update without any issues. So I assume there is no block from Windows. I’m still experiencing this issue even though I’ve added it to the whitelist via Windows Defender. Could you please check if there’s an error in the code?"
contributor: "graphify"
outcome: "useful"
source_nodes: ["launch_installer()", "handoff_command()", ".install()", "UpdateDownload"]
---

# Q: In the Windows application, when I release a new version, I click the ‘Update’ button to install the update, and the new update is downloaded. However, the application then closes and the installer does not launch. By pressing Win + R and then running the downloaded installer from the ‘%temp%’ directory, I am able to install the update without any issues. So I assume there is no block from Windows. I’m still experiencing this issue even though I’ve added it to the whitelist via Windows Defender. Could you please check if there’s an error in the code?

## Answer

Expanded from original query via graph vocab: [updater, update, download, installer, launch, handoff, powershell, window, close, quit, process, job, api, install]. The download succeeds. UpdateDownload.install only confirms that a hidden detached PowerShell process was created; the API then schedules application shutdown after one second. It does not confirm that PowerShell survived shutdown or started Inno Setup. Any downstream failure is invisible except in %TEMP%/parfum-finder-update.log. Releases through v0.2.1 also used a fixed delay; v0.2.2 and later wait for the parent PID, but tests mock Popen and do not execute the handoff on Windows.

## Outcome

- Signal: useful

## Source Nodes

- launch_installer()
- handoff_command()
- .install()
- UpdateDownload