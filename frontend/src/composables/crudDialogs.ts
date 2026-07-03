import { reactive, ref } from 'vue';

// ---------------------------------------------------------------------------
// useCrudDialogs — full create/edit/delete dialog state for a resource.
// ---------------------------------------------------------------------------

export interface UseCrudDialogsOptions<TDto, TForm extends object> {
  /** Fresh form values used when opening the "create" dialog and after reset. */
  defaultForm: TForm;
  /** Extract the numeric id from a DTO (defaults to `(dto as any).id`). */
  getId?: (dto: TDto) => number;
  /** Map a DTO to the fields of the edit form. */
  toForm: (dto: TDto) => Partial<TForm>;
  /** Called when submitting a NEW item. */
  create: (form: TForm) => Promise<unknown> | unknown;
  /** Called when submitting an EDIT. */
  update: (id: number, form: TForm) => Promise<unknown> | unknown;
  /** Called when confirming delete. */
  remove: (id: number) => Promise<unknown> | unknown;
  /**
   * Optional guard: return a truthy string / false to abort submit.
   * If it returns `true` (or nothing), the submit continues.
   */
  validate?: (form: TForm) => boolean | string;
}

/**
 * Encapsulates the boilerplate that shows up any time you have a
 *   "list + create/edit dialog + delete-confirm dialog"
 * pattern (see TaskBoardPage.vue).
 *
 * The composable owns:
 *   - the reactive `form`,
 *   - `editingId` (null → create, number → edit),
 *   - `formDialogOpen` / `deleteDialogOpen`,
 *   - `pendingDeleteId`,
 *   - `openCreateDialog`, `openEditDialog`, `submit`,
 *     `requestDelete`, `confirmDelete`, `resetForm`.
 */
export function useCrudDialogs<TDto, TForm extends object>(
  opts: UseCrudDialogsOptions<TDto, TForm>
) {
  const getId = opts.getId ?? ((dto: TDto) => (dto as any).id as number);

  const form = reactive<TForm>({ ...opts.defaultForm }) as TForm;
  const editingId = ref<number | null>(null);
  const formDialogOpen = ref(false);

  const deleteDialogOpen = ref(false);
  const pendingDeleteId = ref<number | null>(null);

  function assignForm(source: Partial<TForm>): void {
    for (const key of Object.keys(source) as (keyof TForm)[]) {
      (form as any)[key] = source[key];
    }
  }

  function resetForm(): void {
    assignForm(opts.defaultForm);
    editingId.value = null;
  }

  function openCreateDialog(): void {
    resetForm();
    formDialogOpen.value = true;
  }

  function openEditDialog(dto: TDto): void {
    editingId.value = getId(dto);
    // Start from defaults so that fields not present on the DTO are cleared
    assignForm(opts.defaultForm);
    assignForm(opts.toForm(dto));
    formDialogOpen.value = true;
  }

  async function submit(): Promise<void> {
    if (opts.validate) {
      const ok = opts.validate(form);
      if (ok !== true && ok !== undefined) return;
    }
    if (editingId.value === null) {
      await opts.create(form);
    } else {
      await opts.update(editingId.value, form);
    }
    formDialogOpen.value = false;
    resetForm();
  }

  function requestDelete(id?: number): void {
    if (id !== undefined) {
      pendingDeleteId.value = id;
    } else if (editingId.value !== null) {
      pendingDeleteId.value = editingId.value;
    } else {
      return;
    }
    deleteDialogOpen.value = true;
  }

  async function confirmDelete(): Promise<void> {
    if (pendingDeleteId.value != null) {
      await opts.remove(pendingDeleteId.value);
    }
    pendingDeleteId.value = null;
    deleteDialogOpen.value = false;
    formDialogOpen.value = false;
    resetForm();
  }

  return {
    // state
    form,
    editingId,
    formDialogOpen,
    deleteDialogOpen,
    pendingDeleteId,
    // actions
    resetForm,
    openCreateDialog,
    openEditDialog,
    submit,
    requestDelete,
    confirmDelete,
  };
}

// ---------------------------------------------------------------------------
// useDeleteConfirm — lightweight variant for pages that only need a
// "click delete → open confirm dialog → call API" flow (Announcement /
// ReleaseNote management pages).
// ---------------------------------------------------------------------------

export function useDeleteConfirm(remove: (id: number) => Promise<unknown> | unknown) {
  const deleteDialogOpen = ref(false);
  const pendingDeleteId = ref<number | null>(null);

  function requestDelete(id: number): void {
    pendingDeleteId.value = id;
    deleteDialogOpen.value = true;
  }

  async function confirmDelete(): Promise<void> {
    if (pendingDeleteId.value != null) {
      await remove(pendingDeleteId.value);
    }
    pendingDeleteId.value = null;
    deleteDialogOpen.value = false;
  }

  return {
    deleteDialogOpen,
    pendingDeleteId,
    requestDelete,
    confirmDelete,
  };
}
