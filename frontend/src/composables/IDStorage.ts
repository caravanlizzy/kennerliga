// IDStorage.ts

export function useIDStorage() {
  const IDStorage: Record<string, number> = {};

  function addStorageItem(itemId: number, id: number): void {
    IDStorage[itemId.toString()] = id;
  }

  function getStorageItem(itemId: number): number  {
    const item = IDStorage[itemId.toString()];
    return item;
  }

  function removeStorageItem(itemId: number): void {
    delete IDStorage[itemId.toString()];
  }

  return { IDStorage, addStorageItem, getStorageItem, removeStorageItem }
}
