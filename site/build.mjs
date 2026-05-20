import { readFile, writeFile } from "node:fs/promises";
import { transform } from "esbuild";

const inputs = [
  "helpers.jsx",
  "graph-view.jsx",
  "ledger-view.jsx",
  "findings-view.jsx",
  "flow-view.jsx",
  "app.jsx",
];

const parts = [];
for (const path of inputs) {
  const source = await readFile(new URL(path, import.meta.url), "utf8");
  const result = await transform(source, {
    loader: "jsx",
    jsxFactory: "React.createElement",
    jsxFragment: "React.Fragment",
    minify: true,
    sourcemap: false,
    target: "es2020",
    legalComments: "none",
  });
  parts.push(`/* ${path} */\n(()=>{${result.code}\n})();`);
}

await writeFile(new URL("bundle.js", import.meta.url), parts.join("\n") + "\n", "utf8");
