function escapeHtml(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function inline(text) {
  const codes = [];
  let t = text.replace(/`([^`]+)`/g, (_, code) => {
    codes.push(code);
    return "\u0001" + (codes.length - 1) + "\u0001";
  });
  t = t.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  t = t.replace(/(^|[^*])\*([^*]+)\*/g, "$1<em>$2</em>");
  return t.replace(/\u0001(\d+)\u0001/g, (_, index) => "<code>" + codes[+index] + "</code>");
}

function formatMarkdown(text) {
  const raw = escapeHtml(text).split("\n");
  const blocks = [];
  let para = [];
  let list = null;

  const flushPara = () => {
    if (para.length) {
      blocks.push({ type: "p", content: para.join("<br>") });
      para = [];
    }
  };

  const closeList = () => {
    if (list) {
      blocks.push({ type: list.kind, items: list.items });
      list = null;
    }
  };

  for (const line of raw) {
    const item = line.match(/^\s*(?:[-*]|\d+\.)\s+(.*)$/);
    if (item) {
      flushPara();
      const kind = /^\s*\d/.test(line) ? "ol" : "ul";
      if (!list || list.kind !== kind) {
        closeList();
        list = { kind, items: [] };
      }
      list.items.push(item[1]);
      continue;
    }
    closeList();

    const heading = line.match(/^(#{1,3})\s+(.*)$/);
    if (heading) {
      flushPara();
      blocks.push({ type: "h", level: heading[1].length + 1, content: heading[2] });
      continue;
    }

    if (line.trim() === "") {
      flushPara();
      continue;
    }

    para.push(line);
  }
  flushPara();
  closeList();

  return blocks
    .map((block) => {
      if (block.type === "h") return `<h${block.level}>${inline(block.content)}</h${block.level}>`;
      if (block.type === "ul") return `<ul>${block.items.map((i) => `<li>${inline(i)}</li>`).join("")}</ul>`;
      if (block.type === "ol") return `<ol>${block.items.map((i) => `<li>${inline(i)}</li>`).join("")}</ol>`;
      return `<p>${inline(block.content)}</p>`;
    })
    .join("\n");
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { formatMarkdown };
}
