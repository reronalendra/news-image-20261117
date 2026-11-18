// Entry for make.fun "Sum up 17 November's world news in one image".
// The picture is drawn ahead of time (see build_image.py) and shipped
// in this repository, so grading needs no network: this program only
// copies the finished image to the output directory.
import { copyFileSync, existsSync, mkdirSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const MAX_BYTES = 1_048_576; // the image must be at most 1 MiB

const here = dirname(fileURLToPath(import.meta.url));
const source = join(here, "entry.png");
if (!existsSync(source)) {
  throw new Error(`entry.png is missing from the repository (${source})`);
}
const sourceSize = statSync(source).size;
if (sourceSize > MAX_BYTES) {
  throw new Error(
    `entry.png is ${sourceSize} bytes, over the ${MAX_BYTES} byte limit`,
  );
}

const rawOut = process.env.MAKEFUN_OUTPUT_DIR;
const outDir =
  rawOut !== undefined && rawOut.trim() !== "" ? rawOut.trim() : "/output";
try {
  mkdirSync(outDir, { recursive: true });
} catch (err) {
  throw new Error(
    `cannot create output directory ${outDir}: ${(err as Error).message}`,
  );
}

const dest = join(outDir, "entry.png");
try {
  copyFileSync(source, dest);
} catch (err) {
  throw new Error(
    `failed to copy entry.png to ${dest}: ${(err as Error).message}`,
  );
}
if (statSync(dest).size !== sourceSize) {
  throw new Error(`copied entry.png to ${dest} but the size does not match`);
}
console.log(`Wrote entry.png (${sourceSize} bytes) to ${outDir}`);
