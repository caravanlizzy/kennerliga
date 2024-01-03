const SELECTORS = {
  categoryTitle: 'input#id_category-name',
  formCount: '#id_options-TOTAL_FORMS',
};

const addSummaryItem = (text) => {
  let newItem = document.createElement('li');
  newItem.classList.add('list-group-item', 'game-option');
  newItem.innerHTML = text;
  document.getElementById('summary_list').append(newItem);
};

const getNewOptionText = (formCount) => {
  let formNumber = formCount - 1;
  return document.getElementById('id_options-' + formNumber + '-option').value;
};

const getFormInputValue = (formId) => {
  if (formId < 0) return false;
  return document.getElementById('id_options-' + formId + '-option').value;
};

const getFormCount = () => {
  return document.querySelector(SELECTORS.formCount).value;
};
const arePreviousFormsFilled = () => {
  for (let i = 0; i < getFormCount(); i++) {
    if (!getFormInputValue(i)) {
      return false;
    }
  }
  return true;
};

const cloneForm = () => {
  let newForm = document.getElementById('empty_form').innerHTML;
  return newForm.replace(/__prefix__/g, getFormCount());
};

const insertNewForm = () => {
  $('#game_options').append(cloneForm());
};

const updateFormsetVariables = (formCount) => {
  document.querySelector(SELECTORS.formCount).value = (parseInt(formCount) + 1);
};

const onAddClick = () => {
  const formCount = getFormCount();
  if (!arePreviousFormsFilled()) return;
  insertNewForm();
  updateFormsetVariables(formCount);
  const text = getNewOptionText(formCount);
  if (text) {
    addSummaryItem(text);
  }
};

const updateSummaryTitle = () => {
  let newTitle = document.querySelector(SELECTORS.categoryTitle).value;
  document.getElementById('summary_title').innerHTML = newTitle;
};


document.getElementById('add_option_button').addEventListener('click', onAddClick);
document.querySelector(SELECTORS.categoryTitle).addEventListener('change', updateSummaryTitle);
document.querySelector(SELECTORS.categoryTitle).addEventListener('input', updateSummaryTitle);
