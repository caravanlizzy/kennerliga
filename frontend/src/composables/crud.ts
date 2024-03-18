import { Ref, ref } from 'vue';

interface BaseItem {
  id: number | string;
}

export function useCrud<TItem extends BaseItem>(initialItems?: TItem[]) {
  const items = ref([]) as Ref<TItem[]>;
  if (initialItems) {
    items.value.push(...initialItems);
  }

  function addItem(item: TItem) {
    items.value.push(item);
  }

  function deleteItem(itemToRemove: TItem, { uniqueProperty }: {
    uniqueProperty: keyof TItem
  } = { uniqueProperty: 'id' }) {
    items.value = items.value.filter(item => item[uniqueProperty] !== itemToRemove[uniqueProperty]);
  }

  function updateItem(updateItem: TItem, propertyToChange: keyof TItem, newValue: TItem[keyof TItem], { uniqueProperty }: {
    uniqueProperty: keyof TItem
  } = { uniqueProperty: 'id' }) {
    const item = items.value.find(item => item[uniqueProperty] === updateItem.id);
    if (item) {
      item[propertyToChange] = newValue;
    }
  }

  function createRandomNumber(length = 9): number {
    return Math.floor(Math.random() * 10 ** length);
  }

  return { items, addItem, deleteItem, updateItem, createRandomNumber };
}
