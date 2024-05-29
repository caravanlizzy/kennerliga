import { Ref, ref } from 'vue';

interface BaseItem {
  itemId: number | string;
}

export function useItemList<TItem extends BaseItem>(initialItems?: TItem[]) {
  const items = ref([]) as Ref<TItem[]>;
  if (initialItems) {
    items.value.push(...initialItems);
  }

  function addItem(item: TItem) {
    items.value.push(item);
  }

  function deleteItem(itemToRemove: TItem) {
    items.value = items.value.filter(item => item.itemId !== itemToRemove.itemId);
  }

  function updateItem(updateItem: TItem, propertyToChange: keyof TItem, newValue: TItem[keyof TItem]) {
    const item = items.value.find(item => item.itemId === updateItem.itemId);
    if (item) {
      item[propertyToChange] = newValue;
    }
  }

  return { items, addItem, deleteItem, updateItem };
}
