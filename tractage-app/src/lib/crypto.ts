import crypto from 'node:crypto';
import zlib from 'node:zlib';

const VERSION = 2;
const SALT_LENGTH = 16;
const IV_LENGTH = 12;
const TAG_LENGTH = 16;

function deriveKey(passphrase: string, salt: Buffer) {
  return crypto.scryptSync(passphrase, salt, 32);
}

export function encryptBuffer(plain: Buffer, passphrase: string) {
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

export function decryptBuffer(encrypted: Buffer, passphrase: string) {
  const minLength = 1 + SALT_LENGTH + IV_LENGTH + TAG_LENGTH;
  if (encrypted.length <= minLength) {
    throw new Error('Encrypted payload too small.');
  }

  const version = encrypted[0];
  if (version !== VERSION) {
    throw new Error('Unsupported encrypted payload version.');
  }

  let offset = 1;
  const salt = encrypted.subarray(offset, offset + SALT_LENGTH);
  offset += SALT_LENGTH;
  const iv = encrypted.subarray(offset, offset + IV_LENGTH);
  offset += IV_LENGTH;
  const tag = encrypted.subarray(offset, offset + TAG_LENGTH);
  offset += TAG_LENGTH;
  const ciphertext = encrypted.subarray(offset);

  const key = deriveKey(passphrase, salt);
  const decipher = crypto.createDecipheriv('aes-256-gcm', key, iv);
  decipher.setAuthTag(tag);

  const compressed = Buffer.concat([decipher.update(ciphertext), decipher.final()]);
  return zlib.gunzipSync(compressed);
}
