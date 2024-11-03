// IDStorage.ts
const IDStorage: Record<string, number> = {};

export function useIDStorage() {

  function addStorageItem(itemId: number, id: number): void {
    IDStorage[itemId.toString()] = id;
  }

  function getStorageItem(itemId: number): number | undefined {
    const item = IDStorage[itemId.toString()];
    console.log({item})
    return item;
  }

  function removeStorageItem(itemId: number): void {
    delete IDStorage[itemId.toString()];
  }

  return { IDStorage, addStorageItem, getStorageItem, removeStorageItem }
}
