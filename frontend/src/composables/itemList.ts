import { Ref, ref } from 'vue';

interface BaseItem {
  id: number | string;
}

export function useItemList<TItem extends BaseItem>(initialItems?: TItem[]) {
  const items = ref([]) as Ref<TItem[]>;
  if (initialItems) {
    items.value.push(...initialItems);
  }

  function addItem(item: TItem, { prepend = false } = {}) {
    prepend ? items.value.unshift(item) : items.value.push(item);
  }

  function deleteItem(itemToRemove: TItem) {
    items.value = items.value.filter(item => item.id !== itemToRemove.id);
  }

  function updateItem(updateItem: TItem, propertyToChange: keyof TItem, newValue: TItem[keyof TItem]) {
    const item = items.value.find(item => item.id === updateItem.id);
    if (item) {
      item[propertyToChange] = newValue;
    }
  }

  return { items, addItem, deleteItem, updateItem };
}
