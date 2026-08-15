import { createRoot } from "react-dom/client";
import { App } from "./App";
import "./styles.css";

// No StrictMode. It double-invokes effects in development, and one of this
// app's effects opens the WebSocket that *starts* a scan: the second connect
// would be refused with 4409 and the search would sit there dead, in
// development only, for a reason nothing on screen explains.
const root = document.getElementById("root");
if (root === null) throw new Error("no #root to mount into");
createRoot(root).render(<App />);
