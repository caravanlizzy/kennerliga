export function createRandomId(power = 10) {
  return Math.floor(Math.random() * 10 ** power);
}
