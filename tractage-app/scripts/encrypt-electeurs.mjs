import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import zlib from 'node:zlib';

const VERSION = 2;
const SALT_LENGTH = 16;
const IV_LENGTH = 12;
const TAG_LENGTH = 16;

function deriveKey(passphrase, salt) {
  return crypto.scryptSync(passphrase, salt, 32);
}

function encryptBuffer(plain, passphrase) {
  const compressed = zlib.gzipSync(plain);
  const salt = crypto.randomBytes(SALT_LENGTH);
  const iv = crypto.randomBytes(IV_LENGTH);
  const key = deriveKey(passphrase, salt);

  const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);
  const ciphertext = Buffer.concat([cipher.update(compressed), cipher.final()]);
  const tag = cipher.getAuthTag();

  return Buffer.concat([
    Buffer.from([VERSION]),
    salt,
    iv,
    tag,
    ciphertext,
  ]);
}

function parseArg(flag) {
  const index = process.argv.indexOf(flag);
  if (index === -1 || index + 1 >= process.argv.length) return null;
  return process.argv[index + 1];
}

const inputPath = parseArg('--in') || 'public/data/electeurs.csv';
const outputPath = parseArg('--out') || 'public/data/electeurs.enc';
const passphrase = parseArg('--passphrase') || process.env.ELECTEURS_PASSPHRASE;

if (!passphrase) {
  console.error('Missing passphrase. Use --passphrase or ELECTEURS_PASSPHRASE.');
  process.exit(1);
}

const resolvedInput = path.resolve(process.cwd(), inputPath);
const resolvedOutput = path.resolve(process.cwd(), outputPath);

const plain = fs.readFileSync(resolvedInput);
const encrypted = encryptBuffer(plain, passphrase);
fs.writeFileSync(resolvedOutput, encrypted);

console.log(`Encrypted ${inputPath} -> ${outputPath}`);
