const vscode = require("vscode");
const { execFile } = require("child_process");

function activate(context) {
    const runCommand = vscode.commands.registerCommand(
        "gugugaga.runFile",
        () => {
            const editor = vscode.window.activeTextEditor;

            if (!editor) {
                return;
            }

            const filePath = editor.document.uri.fsPath;

            if (!filePath.endsWith(".gugu")) {
                vscode.window.showErrorMessage(
                    "The current file is not a Gugu file."
                );
                return;
            }

            // Check whether the Gugu compiler exists.
            const checkCommand = process.platform === "win32"
                ? "where.exe"
                : "which";

            execFile(checkCommand, ["gugu"], (error) => {
                if (error) {
                    vscode.window.showErrorMessage(
                        "Gugu compiler is not installed."
                    );
                    return;
                }

                // Reuse an existing terminal if one is already open.
                // Prefer the active terminal, otherwise use the first one.
                let terminal =
                    vscode.window.activeTerminal ||
                    vscode.window.terminals[0];

                // Create a terminal only if none are open.
                if (!terminal) {
                    terminal = vscode.window.createTerminal("Gugu");
                }

                terminal.show();

                terminal.sendText(
                    `gugu "${filePath}"`,
                    true
                );
            });
        }
    );

    context.subscriptions.push(runCommand);
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
};