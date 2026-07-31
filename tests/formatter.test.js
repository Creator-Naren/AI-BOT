const { test } = require("node:test");
const assert = require("node:assert");
const { formatMarkdown } = require("../static/js/formatter.js");

test("escapes HTML", () => {
  const out = formatMarkdown("<script>alert(1)</script>");
  assert.ok(!out.includes("<script>"));
  assert.ok(out.includes("&lt;script&gt;"));
});

test("escapes attribute-injection content", () => {
  const out = formatMarkdown('" onmouseover="alert(1)');
  assert.ok(out.includes("&quot; onmouseover=&quot;"));
  assert.ok(!out.includes('" onmouseover="'));
});

test("formats bold and italic", () => {
  assert.strictEqual(formatMarkdown("Hello **world** and *you*"), "<p>Hello <strong>world</strong> and <em>you</em></p>");
});

test("unterminated bold stays literal", () => {
  assert.ok(!formatMarkdown("**oops").includes("<strong>"));
});

test("formats headings", () => {
  const out = formatMarkdown("### Title");
  assert.ok(out.includes("<h4>Title</h4>"));
});

test("formats bullet and numbered lists", () => {
  const out = formatMarkdown("- one\n- two");
  assert.ok(out.includes("<ul>"));
  assert.ok(out.includes("<li>one</li>"));

  const out2 = formatMarkdown("1. first\n2. second");
  assert.ok(out2.includes("<ol>"));
  assert.ok(out2.includes("<li>first</li>"));
});

test("separates mixed list kinds", () => {
  const out = formatMarkdown("- a\n1. b");
  assert.ok(out.includes("<ul>"));
  assert.ok(out.includes("<ol>"));
  assert.ok(out.indexOf("<ul>") < out.indexOf("<ol>"));
});

test("preserves line breaks in paragraphs", () => {
  assert.strictEqual(formatMarkdown("line one\nline two"), "<p>line one<br>line two</p>");
});

test("formats inline code", () => {
  const out = formatMarkdown("run `npm install`");
  assert.ok(out.includes("<code>npm install</code>"));
});

test("protects content inside code spans", () => {
  const out = formatMarkdown("run `**x**`");
  assert.ok(out.includes("<code>**x**</code>"));
  assert.ok(!out.includes("<code><strong>"));
});

test("does not format emphasis inside code spans", () => {
  const out = formatMarkdown("shell glob `*.txt`");
  assert.ok(out.includes("<code>*.txt</code>"));
  assert.ok(!out.includes("<em>"));
});
