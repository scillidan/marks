-- Convert every *.md file under <indir> to a self-contained TeX fragment
-- under <outdir> using the markdown Lua module. The document/section/
-- interblock wrappers emitted by the converter are stripped so that each
-- fragment carries only its own content (paragraph, heading, list, quote...).
--
-- Usage: texlua markdown_block_convert.lua <indir> <outdir>
local kpse = require("kpse")
kpse.set_program_name("luatex")
local markdown = require("markdown")
local lfs = require("lfs")

local indir, outdir = arg[1], arg[2]

local function clean(s)
  s = s:gsub("\\markdownRendererDocumentBegin%s*", "")
  s = s:gsub("\\markdownRendererDocumentEnd%s*", "")
  s = s:gsub("\\markdownRendererSectionBegin%s*", "")
  s = s:gsub("\\markdownRendererSectionEnd%s*", "")
  s = s:gsub("\\markdownRendererInterblockSeparator%s*", "")
  return s
end

local convert = markdown.new({
  eagerCache = false,
  fencedCode = true,
  notes = true,
  underscores = true,
  texMathDollars = false,
})

os.execute('mkdir "' .. outdir .. '" 2>nul')
for file in lfs.dir(indir) do
  if file:match("%.md$") then
    local f = io.open(indir .. "/" .. file, "rb")
    local content = f:read("*a")
    f:close()
    local out = clean(convert(content))
    local o = io.open(outdir .. "/" .. file:gsub("%.md$", ".tex"), "wb")
    o:write(out)
    o:close()
  end
end
