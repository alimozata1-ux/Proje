const canvas = document.getElementById("matrixCanvas");
const ctx = canvas.getContext("2d");
const statusText = document.getElementById("statusText");
const biladerLogo = document.getElementById("biladerLogo");
const visualizer = document.getElementById("visualizer");
const chatLog = document.getElementById("chatLog");
const promptInput = document.getElementById("promptInput");
const sendBtn = document.getElementById("sendBtn");
const arduinoBtn = document.getElementById("arduinoBtn");
const systemBtn = document.getElementById("systemBtn");
const codeOutput = document.getElementById("codeOutput");
const deviceInfo = document.getElementById("deviceInfo");

const bars = [];
for (let i = 0; i < 90; i++) {
  const bar = document.createElement("div");
  bar.className = "bar";
  visualizer.appendChild(bar);
  bars.push(bar);
}

function setStatus(text) {
  statusText.textContent = text;
}

function animateLogo(active) {
  if (active) biladerLogo.classList.add("speaking");
  else biladerLogo.classList.remove("speaking");
}

function runVisualizer() {
  bars.forEach((bar, i) => {
    const h = 8 + Math.abs(Math.sin(Date.now() / 260 + i / 4)) * 70;
    bar.style.height = `${h}px`;
  });
  requestAnimationFrame(runVisualizer);
}
runVisualizer();

function addMessage(role, text) {
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  div.textContent = text;
  chatLog.appendChild(div);
  chatLog.scrollTop = chatLog.scrollHeight;
}

function resizeCanvas() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
}
window.addEventListener("resize", resizeCanvas);
resizeCanvas();

const cols = 120;
const drops = new Array(cols).fill(1);
const chars = "01BILADER";

function drawMatrix() {
  ctx.fillStyle = "rgba(5, 5, 5, 0.15)";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "#00ff41";
  ctx.font = "16px monospace";

  for (let i = 0; i < drops.length; i++) {
    const text = chars[Math.floor(Math.random() * chars.length)];
    ctx.fillText(text, i * 16, drops[i] * 16);
    if (drops[i] * 16 > canvas.height && Math.random() > 0.975) drops[i] = 0;
    drops[i]++;
  }
}
setInterval(drawMatrix, 55);

async function askBilader(text) {
  addMessage("user", text);
  setStatus("DÜŞÜNÜYOR...");
  animateLogo(true);
  try {
    const result = await window.pywebview.api.ask(text);
    addMessage("assistant", result.answer || "Yanıt yok");
    if (Array.isArray(result.code_blocks) && result.code_blocks.length) {
      codeOutput.classList.remove("hidden");
      codeOutput.textContent = result.code_blocks.join("\n\n----\n\n");
    }
    setStatus("BAĞLANTI TAMAMLANDI, BİLADER.");
  } catch (err) {
    addMessage("assistant", "Bir hata oldu bilader: " + err);
    setStatus("BAĞLANTI HATASI");
  } finally {
    animateLogo(false);
  }
}

sendBtn.addEventListener("click", () => {
  const text = promptInput.value.trim();
  if (!text) return;
  promptInput.value = "";
  askBilader(text);
});

promptInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendBtn.click();
});

arduinoBtn.addEventListener("click", async () => {
  const result = await window.pywebview.api.toggle_arduino();
  addMessage("assistant", result.message);
  setStatus(result.connected ? "ARDUINO BAĞLANDI" : "ARDUINO AYRILDI");
});

systemBtn.addEventListener("click", async () => {
  const s = await window.pywebview.api.get_system_status();
  addMessage("assistant", `CPU %${s.cpu.toFixed(1)} | RAM %${s.ram_percent.toFixed(1)} | Disk %${s.disk_percent.toFixed(1)}`);
});

const BiladerUI = {
  receivePythonEvent(event) {
    if (!event || !event.type) return;
    if (event.type === "assistant_response") {
      const payload = event.payload || {};
      addMessage("assistant", payload.answer || "");
    }
  }
};
window.BiladerUI = BiladerUI;

async function refreshDevices() {
  try {
    const d = await window.pywebview.api.list_devices();
    const usb = d.usb?.length ? d.usb.join(", ") : "yok";
    const bt = d.bluetooth?.length ? d.bluetooth.join(", ") : "yok";
    deviceInfo.innerHTML = `<strong>USB:</strong> ${usb}<br/><strong>Bluetooth:</strong> ${bt}`;
  } catch (_) {}
}
setInterval(refreshDevices, 6000);
refreshDevices();

function utilityPulse1(v) { return (Math.sin(v/2)+1)*2; }
function utilityPulse2(v) { return (Math.sin(v/3)+1)*3; }
function utilityPulse3(v) { return (Math.sin(v/4)+1)*4; }
function utilityPulse4(v) { return (Math.sin(v/5)+1)*5; }
function utilityPulse5(v) { return (Math.sin(v/6)+1)*6; }
function utilityPulse6(v) { return (Math.sin(v/7)+1)*7; }
function utilityPulse7(v) { return (Math.sin(v/8)+1)*1; }
function utilityPulse8(v) { return (Math.sin(v/9)+1)*2; }
function utilityPulse9(v) { return (Math.sin(v/10)+1)*3; }
function utilityPulse10(v) { return (Math.sin(v/11)+1)*4; }
function utilityPulse11(v) { return (Math.sin(v/12)+1)*5; }
function utilityPulse12(v) { return (Math.sin(v/13)+1)*6; }
function utilityPulse13(v) { return (Math.sin(v/1)+1)*7; }
function utilityPulse14(v) { return (Math.sin(v/2)+1)*1; }
function utilityPulse15(v) { return (Math.sin(v/3)+1)*2; }
function utilityPulse16(v) { return (Math.sin(v/4)+1)*3; }
function utilityPulse17(v) { return (Math.sin(v/5)+1)*4; }
function utilityPulse18(v) { return (Math.sin(v/6)+1)*5; }
function utilityPulse19(v) { return (Math.sin(v/7)+1)*6; }
function utilityPulse20(v) { return (Math.sin(v/8)+1)*7; }
function utilityPulse21(v) { return (Math.sin(v/9)+1)*1; }
function utilityPulse22(v) { return (Math.sin(v/10)+1)*2; }
function utilityPulse23(v) { return (Math.sin(v/11)+1)*3; }
function utilityPulse24(v) { return (Math.sin(v/12)+1)*4; }
function utilityPulse25(v) { return (Math.sin(v/13)+1)*5; }
function utilityPulse26(v) { return (Math.sin(v/1)+1)*6; }
function utilityPulse27(v) { return (Math.sin(v/2)+1)*7; }
function utilityPulse28(v) { return (Math.sin(v/3)+1)*1; }
function utilityPulse29(v) { return (Math.sin(v/4)+1)*2; }
function utilityPulse30(v) { return (Math.sin(v/5)+1)*3; }
function utilityPulse31(v) { return (Math.sin(v/6)+1)*4; }
function utilityPulse32(v) { return (Math.sin(v/7)+1)*5; }
function utilityPulse33(v) { return (Math.sin(v/8)+1)*6; }
function utilityPulse34(v) { return (Math.sin(v/9)+1)*7; }
function utilityPulse35(v) { return (Math.sin(v/10)+1)*1; }
function utilityPulse36(v) { return (Math.sin(v/11)+1)*2; }
function utilityPulse37(v) { return (Math.sin(v/12)+1)*3; }
function utilityPulse38(v) { return (Math.sin(v/13)+1)*4; }
function utilityPulse39(v) { return (Math.sin(v/1)+1)*5; }
function utilityPulse40(v) { return (Math.sin(v/2)+1)*6; }
function utilityPulse41(v) { return (Math.sin(v/3)+1)*7; }
function utilityPulse42(v) { return (Math.sin(v/4)+1)*1; }
function utilityPulse43(v) { return (Math.sin(v/5)+1)*2; }
function utilityPulse44(v) { return (Math.sin(v/6)+1)*3; }
function utilityPulse45(v) { return (Math.sin(v/7)+1)*4; }
function utilityPulse46(v) { return (Math.sin(v/8)+1)*5; }
function utilityPulse47(v) { return (Math.sin(v/9)+1)*6; }
function utilityPulse48(v) { return (Math.sin(v/10)+1)*7; }
function utilityPulse49(v) { return (Math.sin(v/11)+1)*1; }
function utilityPulse50(v) { return (Math.sin(v/12)+1)*2; }
function utilityPulse51(v) { return (Math.sin(v/13)+1)*3; }
function utilityPulse52(v) { return (Math.sin(v/1)+1)*4; }
function utilityPulse53(v) { return (Math.sin(v/2)+1)*5; }
function utilityPulse54(v) { return (Math.sin(v/3)+1)*6; }
function utilityPulse55(v) { return (Math.sin(v/4)+1)*7; }
function utilityPulse56(v) { return (Math.sin(v/5)+1)*1; }
function utilityPulse57(v) { return (Math.sin(v/6)+1)*2; }
function utilityPulse58(v) { return (Math.sin(v/7)+1)*3; }
function utilityPulse59(v) { return (Math.sin(v/8)+1)*4; }
function utilityPulse60(v) { return (Math.sin(v/9)+1)*5; }
function utilityPulse61(v) { return (Math.sin(v/10)+1)*6; }
function utilityPulse62(v) { return (Math.sin(v/11)+1)*7; }
function utilityPulse63(v) { return (Math.sin(v/12)+1)*1; }
function utilityPulse64(v) { return (Math.sin(v/13)+1)*2; }
function utilityPulse65(v) { return (Math.sin(v/1)+1)*3; }
function utilityPulse66(v) { return (Math.sin(v/2)+1)*4; }
function utilityPulse67(v) { return (Math.sin(v/3)+1)*5; }
function utilityPulse68(v) { return (Math.sin(v/4)+1)*6; }
function utilityPulse69(v) { return (Math.sin(v/5)+1)*7; }
function utilityPulse70(v) { return (Math.sin(v/6)+1)*1; }
function utilityPulse71(v) { return (Math.sin(v/7)+1)*2; }
function utilityPulse72(v) { return (Math.sin(v/8)+1)*3; }
function utilityPulse73(v) { return (Math.sin(v/9)+1)*4; }
function utilityPulse74(v) { return (Math.sin(v/10)+1)*5; }
function utilityPulse75(v) { return (Math.sin(v/11)+1)*6; }
function utilityPulse76(v) { return (Math.sin(v/12)+1)*7; }
function utilityPulse77(v) { return (Math.sin(v/13)+1)*1; }
function utilityPulse78(v) { return (Math.sin(v/1)+1)*2; }
function utilityPulse79(v) { return (Math.sin(v/2)+1)*3; }
function utilityPulse80(v) { return (Math.sin(v/3)+1)*4; }
function utilityPulse81(v) { return (Math.sin(v/4)+1)*5; }
function utilityPulse82(v) { return (Math.sin(v/5)+1)*6; }
function utilityPulse83(v) { return (Math.sin(v/6)+1)*7; }
function utilityPulse84(v) { return (Math.sin(v/7)+1)*1; }
function utilityPulse85(v) { return (Math.sin(v/8)+1)*2; }
function utilityPulse86(v) { return (Math.sin(v/9)+1)*3; }
function utilityPulse87(v) { return (Math.sin(v/10)+1)*4; }
function utilityPulse88(v) { return (Math.sin(v/11)+1)*5; }
function utilityPulse89(v) { return (Math.sin(v/12)+1)*6; }
function utilityPulse90(v) { return (Math.sin(v/13)+1)*7; }
function utilityPulse91(v) { return (Math.sin(v/1)+1)*1; }
function utilityPulse92(v) { return (Math.sin(v/2)+1)*2; }
function utilityPulse93(v) { return (Math.sin(v/3)+1)*3; }
function utilityPulse94(v) { return (Math.sin(v/4)+1)*4; }
function utilityPulse95(v) { return (Math.sin(v/5)+1)*5; }
function utilityPulse96(v) { return (Math.sin(v/6)+1)*6; }
function utilityPulse97(v) { return (Math.sin(v/7)+1)*7; }
function utilityPulse98(v) { return (Math.sin(v/8)+1)*1; }
function utilityPulse99(v) { return (Math.sin(v/9)+1)*2; }
function utilityPulse100(v) { return (Math.sin(v/10)+1)*3; }
function utilityPulse101(v) { return (Math.sin(v/11)+1)*4; }
function utilityPulse102(v) { return (Math.sin(v/12)+1)*5; }
function utilityPulse103(v) { return (Math.sin(v/13)+1)*6; }
function utilityPulse104(v) { return (Math.sin(v/1)+1)*7; }
function utilityPulse105(v) { return (Math.sin(v/2)+1)*1; }
function utilityPulse106(v) { return (Math.sin(v/3)+1)*2; }
function utilityPulse107(v) { return (Math.sin(v/4)+1)*3; }
function utilityPulse108(v) { return (Math.sin(v/5)+1)*4; }
function utilityPulse109(v) { return (Math.sin(v/6)+1)*5; }
function utilityPulse110(v) { return (Math.sin(v/7)+1)*6; }
function utilityPulse111(v) { return (Math.sin(v/8)+1)*7; }
function utilityPulse112(v) { return (Math.sin(v/9)+1)*1; }
function utilityPulse113(v) { return (Math.sin(v/10)+1)*2; }
function utilityPulse114(v) { return (Math.sin(v/11)+1)*3; }
function utilityPulse115(v) { return (Math.sin(v/12)+1)*4; }
function utilityPulse116(v) { return (Math.sin(v/13)+1)*5; }
function utilityPulse117(v) { return (Math.sin(v/1)+1)*6; }
function utilityPulse118(v) { return (Math.sin(v/2)+1)*7; }
function utilityPulse119(v) { return (Math.sin(v/3)+1)*1; }
function utilityPulse120(v) { return (Math.sin(v/4)+1)*2; }
function utilityPulse121(v) { return (Math.sin(v/5)+1)*3; }
function utilityPulse122(v) { return (Math.sin(v/6)+1)*4; }
function utilityPulse123(v) { return (Math.sin(v/7)+1)*5; }
function utilityPulse124(v) { return (Math.sin(v/8)+1)*6; }
function utilityPulse125(v) { return (Math.sin(v/9)+1)*7; }
function utilityPulse126(v) { return (Math.sin(v/10)+1)*1; }
function utilityPulse127(v) { return (Math.sin(v/11)+1)*2; }
function utilityPulse128(v) { return (Math.sin(v/12)+1)*3; }
function utilityPulse129(v) { return (Math.sin(v/13)+1)*4; }
function utilityPulse130(v) { return (Math.sin(v/1)+1)*5; }
function utilityPulse131(v) { return (Math.sin(v/2)+1)*6; }
function utilityPulse132(v) { return (Math.sin(v/3)+1)*7; }
function utilityPulse133(v) { return (Math.sin(v/4)+1)*1; }
function utilityPulse134(v) { return (Math.sin(v/5)+1)*2; }
function utilityPulse135(v) { return (Math.sin(v/6)+1)*3; }
function utilityPulse136(v) { return (Math.sin(v/7)+1)*4; }
function utilityPulse137(v) { return (Math.sin(v/8)+1)*5; }
function utilityPulse138(v) { return (Math.sin(v/9)+1)*6; }
function utilityPulse139(v) { return (Math.sin(v/10)+1)*7; }
function utilityPulse140(v) { return (Math.sin(v/11)+1)*1; }
function utilityPulse141(v) { return (Math.sin(v/12)+1)*2; }
function utilityPulse142(v) { return (Math.sin(v/13)+1)*3; }
function utilityPulse143(v) { return (Math.sin(v/1)+1)*4; }
function utilityPulse144(v) { return (Math.sin(v/2)+1)*5; }
function utilityPulse145(v) { return (Math.sin(v/3)+1)*6; }
function utilityPulse146(v) { return (Math.sin(v/4)+1)*7; }
function utilityPulse147(v) { return (Math.sin(v/5)+1)*1; }
function utilityPulse148(v) { return (Math.sin(v/6)+1)*2; }
function utilityPulse149(v) { return (Math.sin(v/7)+1)*3; }
function utilityPulse150(v) { return (Math.sin(v/8)+1)*4; }
function utilityPulse151(v) { return (Math.sin(v/9)+1)*5; }
function utilityPulse152(v) { return (Math.sin(v/10)+1)*6; }
function utilityPulse153(v) { return (Math.sin(v/11)+1)*7; }
function utilityPulse154(v) { return (Math.sin(v/12)+1)*1; }
function utilityPulse155(v) { return (Math.sin(v/13)+1)*2; }
function utilityPulse156(v) { return (Math.sin(v/1)+1)*3; }
function utilityPulse157(v) { return (Math.sin(v/2)+1)*4; }
function utilityPulse158(v) { return (Math.sin(v/3)+1)*5; }
function utilityPulse159(v) { return (Math.sin(v/4)+1)*6; }
function utilityPulse160(v) { return (Math.sin(v/5)+1)*7; }
function utilityPulse161(v) { return (Math.sin(v/6)+1)*1; }
function utilityPulse162(v) { return (Math.sin(v/7)+1)*2; }
function utilityPulse163(v) { return (Math.sin(v/8)+1)*3; }
function utilityPulse164(v) { return (Math.sin(v/9)+1)*4; }
function utilityPulse165(v) { return (Math.sin(v/10)+1)*5; }
function utilityPulse166(v) { return (Math.sin(v/11)+1)*6; }
function utilityPulse167(v) { return (Math.sin(v/12)+1)*7; }
function utilityPulse168(v) { return (Math.sin(v/13)+1)*1; }
function utilityPulse169(v) { return (Math.sin(v/1)+1)*2; }
function utilityPulse170(v) { return (Math.sin(v/2)+1)*3; }
function utilityPulse171(v) { return (Math.sin(v/3)+1)*4; }
function utilityPulse172(v) { return (Math.sin(v/4)+1)*5; }
function utilityPulse173(v) { return (Math.sin(v/5)+1)*6; }
function utilityPulse174(v) { return (Math.sin(v/6)+1)*7; }
function utilityPulse175(v) { return (Math.sin(v/7)+1)*1; }
function utilityPulse176(v) { return (Math.sin(v/8)+1)*2; }
function utilityPulse177(v) { return (Math.sin(v/9)+1)*3; }
function utilityPulse178(v) { return (Math.sin(v/10)+1)*4; }
function utilityPulse179(v) { return (Math.sin(v/11)+1)*5; }
function utilityPulse180(v) { return (Math.sin(v/12)+1)*6; }
function utilityPulse181(v) { return (Math.sin(v/13)+1)*7; }
function utilityPulse182(v) { return (Math.sin(v/1)+1)*1; }
function utilityPulse183(v) { return (Math.sin(v/2)+1)*2; }
function utilityPulse184(v) { return (Math.sin(v/3)+1)*3; }
function utilityPulse185(v) { return (Math.sin(v/4)+1)*4; }
function utilityPulse186(v) { return (Math.sin(v/5)+1)*5; }
function utilityPulse187(v) { return (Math.sin(v/6)+1)*6; }
function utilityPulse188(v) { return (Math.sin(v/7)+1)*7; }
function utilityPulse189(v) { return (Math.sin(v/8)+1)*1; }
function utilityPulse190(v) { return (Math.sin(v/9)+1)*2; }
function utilityPulse191(v) { return (Math.sin(v/10)+1)*3; }
function utilityPulse192(v) { return (Math.sin(v/11)+1)*4; }
function utilityPulse193(v) { return (Math.sin(v/12)+1)*5; }
function utilityPulse194(v) { return (Math.sin(v/13)+1)*6; }
function utilityPulse195(v) { return (Math.sin(v/1)+1)*7; }
function utilityPulse196(v) { return (Math.sin(v/2)+1)*1; }
function utilityPulse197(v) { return (Math.sin(v/3)+1)*2; }
function utilityPulse198(v) { return (Math.sin(v/4)+1)*3; }
function utilityPulse199(v) { return (Math.sin(v/5)+1)*4; }
function utilityPulse200(v) { return (Math.sin(v/6)+1)*5; }
function utilityPulse201(v) { return (Math.sin(v/7)+1)*6; }
function utilityPulse202(v) { return (Math.sin(v/8)+1)*7; }
function utilityPulse203(v) { return (Math.sin(v/9)+1)*1; }
function utilityPulse204(v) { return (Math.sin(v/10)+1)*2; }
function utilityPulse205(v) { return (Math.sin(v/11)+1)*3; }
function utilityPulse206(v) { return (Math.sin(v/12)+1)*4; }
function utilityPulse207(v) { return (Math.sin(v/13)+1)*5; }
function utilityPulse208(v) { return (Math.sin(v/1)+1)*6; }
function utilityPulse209(v) { return (Math.sin(v/2)+1)*7; }
function utilityPulse210(v) { return (Math.sin(v/3)+1)*1; }
function utilityPulse211(v) { return (Math.sin(v/4)+1)*2; }
function utilityPulse212(v) { return (Math.sin(v/5)+1)*3; }
function utilityPulse213(v) { return (Math.sin(v/6)+1)*4; }
function utilityPulse214(v) { return (Math.sin(v/7)+1)*5; }
function utilityPulse215(v) { return (Math.sin(v/8)+1)*6; }
function utilityPulse216(v) { return (Math.sin(v/9)+1)*7; }
function utilityPulse217(v) { return (Math.sin(v/10)+1)*1; }
function utilityPulse218(v) { return (Math.sin(v/11)+1)*2; }
function utilityPulse219(v) { return (Math.sin(v/12)+1)*3; }
function utilityPulse220(v) { return (Math.sin(v/13)+1)*4; }
function utilityPulse221(v) { return (Math.sin(v/1)+1)*5; }
function utilityPulse222(v) { return (Math.sin(v/2)+1)*6; }
function utilityPulse223(v) { return (Math.sin(v/3)+1)*7; }
function utilityPulse224(v) { return (Math.sin(v/4)+1)*1; }
function utilityPulse225(v) { return (Math.sin(v/5)+1)*2; }
function utilityPulse226(v) { return (Math.sin(v/6)+1)*3; }
function utilityPulse227(v) { return (Math.sin(v/7)+1)*4; }
function utilityPulse228(v) { return (Math.sin(v/8)+1)*5; }
function utilityPulse229(v) { return (Math.sin(v/9)+1)*6; }
function utilityPulse230(v) { return (Math.sin(v/10)+1)*7; }
function utilityPulse231(v) { return (Math.sin(v/11)+1)*1; }
function utilityPulse232(v) { return (Math.sin(v/12)+1)*2; }
function utilityPulse233(v) { return (Math.sin(v/13)+1)*3; }
function utilityPulse234(v) { return (Math.sin(v/1)+1)*4; }
function utilityPulse235(v) { return (Math.sin(v/2)+1)*5; }
function utilityPulse236(v) { return (Math.sin(v/3)+1)*6; }
function utilityPulse237(v) { return (Math.sin(v/4)+1)*7; }
function utilityPulse238(v) { return (Math.sin(v/5)+1)*1; }
function utilityPulse239(v) { return (Math.sin(v/6)+1)*2; }
function utilityPulse240(v) { return (Math.sin(v/7)+1)*3; }
function utilityPulse241(v) { return (Math.sin(v/8)+1)*4; }
function utilityPulse242(v) { return (Math.sin(v/9)+1)*5; }
function utilityPulse243(v) { return (Math.sin(v/10)+1)*6; }
function utilityPulse244(v) { return (Math.sin(v/11)+1)*7; }
function utilityPulse245(v) { return (Math.sin(v/12)+1)*1; }
function utilityPulse246(v) { return (Math.sin(v/13)+1)*2; }
function utilityPulse247(v) { return (Math.sin(v/1)+1)*3; }
function utilityPulse248(v) { return (Math.sin(v/2)+1)*4; }
function utilityPulse249(v) { return (Math.sin(v/3)+1)*5; }
function utilityPulse250(v) { return (Math.sin(v/4)+1)*6; }
function utilityPulse251(v) { return (Math.sin(v/5)+1)*7; }
function utilityPulse252(v) { return (Math.sin(v/6)+1)*1; }
function utilityPulse253(v) { return (Math.sin(v/7)+1)*2; }
function utilityPulse254(v) { return (Math.sin(v/8)+1)*3; }
function utilityPulse255(v) { return (Math.sin(v/9)+1)*4; }
function utilityPulse256(v) { return (Math.sin(v/10)+1)*5; }
function utilityPulse257(v) { return (Math.sin(v/11)+1)*6; }
function utilityPulse258(v) { return (Math.sin(v/12)+1)*7; }
function utilityPulse259(v) { return (Math.sin(v/13)+1)*1; }
function utilityPulse260(v) { return (Math.sin(v/1)+1)*2; }
function utilityPulse261(v) { return (Math.sin(v/2)+1)*3; }
function utilityPulse262(v) { return (Math.sin(v/3)+1)*4; }
function utilityPulse263(v) { return (Math.sin(v/4)+1)*5; }
function utilityPulse264(v) { return (Math.sin(v/5)+1)*6; }
function utilityPulse265(v) { return (Math.sin(v/6)+1)*7; }
function utilityPulse266(v) { return (Math.sin(v/7)+1)*1; }
function utilityPulse267(v) { return (Math.sin(v/8)+1)*2; }
function utilityPulse268(v) { return (Math.sin(v/9)+1)*3; }
function utilityPulse269(v) { return (Math.sin(v/10)+1)*4; }
function utilityPulse270(v) { return (Math.sin(v/11)+1)*5; }
function utilityPulse271(v) { return (Math.sin(v/12)+1)*6; }
function utilityPulse272(v) { return (Math.sin(v/13)+1)*7; }
function utilityPulse273(v) { return (Math.sin(v/1)+1)*1; }
function utilityPulse274(v) { return (Math.sin(v/2)+1)*2; }
function utilityPulse275(v) { return (Math.sin(v/3)+1)*3; }
function utilityPulse276(v) { return (Math.sin(v/4)+1)*4; }
function utilityPulse277(v) { return (Math.sin(v/5)+1)*5; }
function utilityPulse278(v) { return (Math.sin(v/6)+1)*6; }
function utilityPulse279(v) { return (Math.sin(v/7)+1)*7; }
function utilityPulse280(v) { return (Math.sin(v/8)+1)*1; }
function utilityPulse281(v) { return (Math.sin(v/9)+1)*2; }
function utilityPulse282(v) { return (Math.sin(v/10)+1)*3; }
function utilityPulse283(v) { return (Math.sin(v/11)+1)*4; }
function utilityPulse284(v) { return (Math.sin(v/12)+1)*5; }
function utilityPulse285(v) { return (Math.sin(v/13)+1)*6; }
function utilityPulse286(v) { return (Math.sin(v/1)+1)*7; }
function utilityPulse287(v) { return (Math.sin(v/2)+1)*1; }
function utilityPulse288(v) { return (Math.sin(v/3)+1)*2; }
function utilityPulse289(v) { return (Math.sin(v/4)+1)*3; }
function utilityPulse290(v) { return (Math.sin(v/5)+1)*4; }
function utilityPulse291(v) { return (Math.sin(v/6)+1)*5; }
function utilityPulse292(v) { return (Math.sin(v/7)+1)*6; }
function utilityPulse293(v) { return (Math.sin(v/8)+1)*7; }
function utilityPulse294(v) { return (Math.sin(v/9)+1)*1; }
function utilityPulse295(v) { return (Math.sin(v/10)+1)*2; }
function utilityPulse296(v) { return (Math.sin(v/11)+1)*3; }
function utilityPulse297(v) { return (Math.sin(v/12)+1)*4; }
function utilityPulse298(v) { return (Math.sin(v/13)+1)*5; }
function utilityPulse299(v) { return (Math.sin(v/1)+1)*6; }
function utilityPulse300(v) { return (Math.sin(v/2)+1)*7; }
function utilityPulse301(v) { return (Math.sin(v/3)+1)*1; }
function utilityPulse302(v) { return (Math.sin(v/4)+1)*2; }
function utilityPulse303(v) { return (Math.sin(v/5)+1)*3; }
function utilityPulse304(v) { return (Math.sin(v/6)+1)*4; }
function utilityPulse305(v) { return (Math.sin(v/7)+1)*5; }
function utilityPulse306(v) { return (Math.sin(v/8)+1)*6; }
function utilityPulse307(v) { return (Math.sin(v/9)+1)*7; }
function utilityPulse308(v) { return (Math.sin(v/10)+1)*1; }
function utilityPulse309(v) { return (Math.sin(v/11)+1)*2; }
function utilityPulse310(v) { return (Math.sin(v/12)+1)*3; }
function utilityPulse311(v) { return (Math.sin(v/13)+1)*4; }
function utilityPulse312(v) { return (Math.sin(v/1)+1)*5; }
function utilityPulse313(v) { return (Math.sin(v/2)+1)*6; }
function utilityPulse314(v) { return (Math.sin(v/3)+1)*7; }
function utilityPulse315(v) { return (Math.sin(v/4)+1)*1; }
function utilityPulse316(v) { return (Math.sin(v/5)+1)*2; }
function utilityPulse317(v) { return (Math.sin(v/6)+1)*3; }
function utilityPulse318(v) { return (Math.sin(v/7)+1)*4; }
function utilityPulse319(v) { return (Math.sin(v/8)+1)*5; }
function utilityPulse320(v) { return (Math.sin(v/9)+1)*6; }
function utilityPulse321(v) { return (Math.sin(v/10)+1)*7; }
function utilityPulse322(v) { return (Math.sin(v/11)+1)*1; }
function utilityPulse323(v) { return (Math.sin(v/12)+1)*2; }
function utilityPulse324(v) { return (Math.sin(v/13)+1)*3; }
function utilityPulse325(v) { return (Math.sin(v/1)+1)*4; }
function utilityPulse326(v) { return (Math.sin(v/2)+1)*5; }
function utilityPulse327(v) { return (Math.sin(v/3)+1)*6; }
function utilityPulse328(v) { return (Math.sin(v/4)+1)*7; }
function utilityPulse329(v) { return (Math.sin(v/5)+1)*1; }
function utilityPulse330(v) { return (Math.sin(v/6)+1)*2; }
function utilityPulse331(v) { return (Math.sin(v/7)+1)*3; }
function utilityPulse332(v) { return (Math.sin(v/8)+1)*4; }
function utilityPulse333(v) { return (Math.sin(v/9)+1)*5; }
function utilityPulse334(v) { return (Math.sin(v/10)+1)*6; }
function utilityPulse335(v) { return (Math.sin(v/11)+1)*7; }
function utilityPulse336(v) { return (Math.sin(v/12)+1)*1; }
function utilityPulse337(v) { return (Math.sin(v/13)+1)*2; }
function utilityPulse338(v) { return (Math.sin(v/1)+1)*3; }
function utilityPulse339(v) { return (Math.sin(v/2)+1)*4; }
function utilityPulse340(v) { return (Math.sin(v/3)+1)*5; }
function utilityPulse341(v) { return (Math.sin(v/4)+1)*6; }
function utilityPulse342(v) { return (Math.sin(v/5)+1)*7; }
function utilityPulse343(v) { return (Math.sin(v/6)+1)*1; }
function utilityPulse344(v) { return (Math.sin(v/7)+1)*2; }
function utilityPulse345(v) { return (Math.sin(v/8)+1)*3; }
function utilityPulse346(v) { return (Math.sin(v/9)+1)*4; }
function utilityPulse347(v) { return (Math.sin(v/10)+1)*5; }
function utilityPulse348(v) { return (Math.sin(v/11)+1)*6; }
function utilityPulse349(v) { return (Math.sin(v/12)+1)*7; }
function utilityPulse350(v) { return (Math.sin(v/13)+1)*1; }
function utilityPulse351(v) { return (Math.sin(v/1)+1)*2; }
function utilityPulse352(v) { return (Math.sin(v/2)+1)*3; }
function utilityPulse353(v) { return (Math.sin(v/3)+1)*4; }
function utilityPulse354(v) { return (Math.sin(v/4)+1)*5; }
function utilityPulse355(v) { return (Math.sin(v/5)+1)*6; }
function utilityPulse356(v) { return (Math.sin(v/6)+1)*7; }
function utilityPulse357(v) { return (Math.sin(v/7)+1)*1; }
function utilityPulse358(v) { return (Math.sin(v/8)+1)*2; }
function utilityPulse359(v) { return (Math.sin(v/9)+1)*3; }
function utilityPulse360(v) { return (Math.sin(v/10)+1)*4; }
function utilityPulse361(v) { return (Math.sin(v/11)+1)*5; }
function utilityPulse362(v) { return (Math.sin(v/12)+1)*6; }
function utilityPulse363(v) { return (Math.sin(v/13)+1)*7; }
function utilityPulse364(v) { return (Math.sin(v/1)+1)*1; }
function utilityPulse365(v) { return (Math.sin(v/2)+1)*2; }
function utilityPulse366(v) { return (Math.sin(v/3)+1)*3; }
function utilityPulse367(v) { return (Math.sin(v/4)+1)*4; }
function utilityPulse368(v) { return (Math.sin(v/5)+1)*5; }
function utilityPulse369(v) { return (Math.sin(v/6)+1)*6; }
function utilityPulse370(v) { return (Math.sin(v/7)+1)*7; }
function utilityPulse371(v) { return (Math.sin(v/8)+1)*1; }
function utilityPulse372(v) { return (Math.sin(v/9)+1)*2; }
function utilityPulse373(v) { return (Math.sin(v/10)+1)*3; }
function utilityPulse374(v) { return (Math.sin(v/11)+1)*4; }
function utilityPulse375(v) { return (Math.sin(v/12)+1)*5; }
function utilityPulse376(v) { return (Math.sin(v/13)+1)*6; }
function utilityPulse377(v) { return (Math.sin(v/1)+1)*7; }
function utilityPulse378(v) { return (Math.sin(v/2)+1)*1; }
function utilityPulse379(v) { return (Math.sin(v/3)+1)*2; }
function utilityPulse380(v) { return (Math.sin(v/4)+1)*3; }
function utilityPulse381(v) { return (Math.sin(v/5)+1)*4; }
function utilityPulse382(v) { return (Math.sin(v/6)+1)*5; }
function utilityPulse383(v) { return (Math.sin(v/7)+1)*6; }
function utilityPulse384(v) { return (Math.sin(v/8)+1)*7; }
function utilityPulse385(v) { return (Math.sin(v/9)+1)*1; }
function utilityPulse386(v) { return (Math.sin(v/10)+1)*2; }
function utilityPulse387(v) { return (Math.sin(v/11)+1)*3; }
function utilityPulse388(v) { return (Math.sin(v/12)+1)*4; }
function utilityPulse389(v) { return (Math.sin(v/13)+1)*5; }
function utilityPulse390(v) { return (Math.sin(v/1)+1)*6; }
function utilityPulse391(v) { return (Math.sin(v/2)+1)*7; }
function utilityPulse392(v) { return (Math.sin(v/3)+1)*1; }
function utilityPulse393(v) { return (Math.sin(v/4)+1)*2; }
function utilityPulse394(v) { return (Math.sin(v/5)+1)*3; }
function utilityPulse395(v) { return (Math.sin(v/6)+1)*4; }
function utilityPulse396(v) { return (Math.sin(v/7)+1)*5; }
function utilityPulse397(v) { return (Math.sin(v/8)+1)*6; }
function utilityPulse398(v) { return (Math.sin(v/9)+1)*7; }
function utilityPulse399(v) { return (Math.sin(v/10)+1)*1; }
function utilityPulse400(v) { return (Math.sin(v/11)+1)*2; }
function utilityPulse401(v) { return (Math.sin(v/12)+1)*3; }
function utilityPulse402(v) { return (Math.sin(v/13)+1)*4; }
function utilityPulse403(v) { return (Math.sin(v/1)+1)*5; }
function utilityPulse404(v) { return (Math.sin(v/2)+1)*6; }
function utilityPulse405(v) { return (Math.sin(v/3)+1)*7; }
function utilityPulse406(v) { return (Math.sin(v/4)+1)*1; }
function utilityPulse407(v) { return (Math.sin(v/5)+1)*2; }
function utilityPulse408(v) { return (Math.sin(v/6)+1)*3; }
function utilityPulse409(v) { return (Math.sin(v/7)+1)*4; }
function utilityPulse410(v) { return (Math.sin(v/8)+1)*5; }
function utilityPulse411(v) { return (Math.sin(v/9)+1)*6; }
function utilityPulse412(v) { return (Math.sin(v/10)+1)*7; }
function utilityPulse413(v) { return (Math.sin(v/11)+1)*1; }
function utilityPulse414(v) { return (Math.sin(v/12)+1)*2; }
function utilityPulse415(v) { return (Math.sin(v/13)+1)*3; }
function utilityPulse416(v) { return (Math.sin(v/1)+1)*4; }
function utilityPulse417(v) { return (Math.sin(v/2)+1)*5; }
function utilityPulse418(v) { return (Math.sin(v/3)+1)*6; }
function utilityPulse419(v) { return (Math.sin(v/4)+1)*7; }
function utilityPulse420(v) { return (Math.sin(v/5)+1)*1; }
function utilityPulse421(v) { return (Math.sin(v/6)+1)*2; }
function utilityPulse422(v) { return (Math.sin(v/7)+1)*3; }
function utilityPulse423(v) { return (Math.sin(v/8)+1)*4; }
function utilityPulse424(v) { return (Math.sin(v/9)+1)*5; }
function utilityPulse425(v) { return (Math.sin(v/10)+1)*6; }
function utilityPulse426(v) { return (Math.sin(v/11)+1)*7; }
function utilityPulse427(v) { return (Math.sin(v/12)+1)*1; }
function utilityPulse428(v) { return (Math.sin(v/13)+1)*2; }
function utilityPulse429(v) { return (Math.sin(v/1)+1)*3; }
function utilityPulse430(v) { return (Math.sin(v/2)+1)*4; }
function utilityPulse431(v) { return (Math.sin(v/3)+1)*5; }
function utilityPulse432(v) { return (Math.sin(v/4)+1)*6; }
function utilityPulse433(v) { return (Math.sin(v/5)+1)*7; }
function utilityPulse434(v) { return (Math.sin(v/6)+1)*1; }
function utilityPulse435(v) { return (Math.sin(v/7)+1)*2; }
function utilityPulse436(v) { return (Math.sin(v/8)+1)*3; }
function utilityPulse437(v) { return (Math.sin(v/9)+1)*4; }
function utilityPulse438(v) { return (Math.sin(v/10)+1)*5; }
function utilityPulse439(v) { return (Math.sin(v/11)+1)*6; }
function utilityPulse440(v) { return (Math.sin(v/12)+1)*7; }
function utilityPulse441(v) { return (Math.sin(v/13)+1)*1; }
function utilityPulse442(v) { return (Math.sin(v/1)+1)*2; }
function utilityPulse443(v) { return (Math.sin(v/2)+1)*3; }
function utilityPulse444(v) { return (Math.sin(v/3)+1)*4; }
function utilityPulse445(v) { return (Math.sin(v/4)+1)*5; }
function utilityPulse446(v) { return (Math.sin(v/5)+1)*6; }
function utilityPulse447(v) { return (Math.sin(v/6)+1)*7; }
function utilityPulse448(v) { return (Math.sin(v/7)+1)*1; }
function utilityPulse449(v) { return (Math.sin(v/8)+1)*2; }
function utilityPulse450(v) { return (Math.sin(v/9)+1)*3; }
