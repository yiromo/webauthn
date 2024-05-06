const BASE_URL = 'http://localhost:8100'; // Base URL for backend API requests

const { startRegistration, startAuthentication } = SimpleWebAuthnBrowser;

const statusRegister = document.getElementById("statusRegister");
const dbgRegister = document.getElementById("dbgRegister");

function printToDebug(elemDebug, title, output) {
  if (elemDebug.innerHTML !== "") {
    elemDebug.innerHTML += "\n";
  }
  elemDebug.innerHTML += `// ${title}\n`;
  elemDebug.innerHTML += `${output}\n`;
}

function resetDebug(elemDebug) {
  elemDebug.innerHTML = "";
}

function printToStatus(elemStatus, output) {
  elemStatus.innerHTML = output;
}

function resetStatus(elemStatus) {
  elemStatus.innerHTML = "";
}

function getPassStatus() {
  return "✅";
}
function getFailureStatus(message) {
  return `🛑 (Reason: ${message})`;
}

document
  .getElementById("registerbtn")
  .addEventListener("click", async () => {
    resetStatus(statusRegister);
    resetDebug(dbgRegister);

    // Get options
    const resp = await fetch(`${BASE_URL}/webauth/register_options`);
    const opts = await resp.json();
    printToDebug(
      dbgRegister,
      "Registration Options",
      JSON.stringify(opts, null, 2)
    );

    // Start WebAuthn Registration
    let regResp;
    try {
      regResp = await startRegistration(opts);
      printToDebug(
        dbgRegister,
        "Registration Response",
        JSON.stringify(regResp, null, 2)
      );
    } catch (err) {
      printToStatus(statusRegister, getFailureStatus(err));
      throw new Error(err);
    }

    // Send response to server
    const verificationResp = await fetch(
      `${BASE_URL}/webauth/verify_registration`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(regResp),
      }
    );

    // Report validation response
    const verificationRespJSON = await verificationResp.json();
    const { verified, msg } = verificationRespJSON;
    if (verified) {
      printToStatus(statusRegister, getPassStatus());
    } else {
      printToStatus(statusRegister, getFailureStatus(msg));
    }
    printToDebug(
      dbgRegister,
      "Verification Response",
      JSON.stringify(verificationRespJSON, null, 2)
    );
  });