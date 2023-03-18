// const addOption = (text) => {
//   let newItem = document.createElement('div');
//   newItem.classList.add('p-2');
//   newItem.innerHTML = '- ' + text;
//   document.getElementById('game_options').append(newItem);
// };

const addSummaryItem = (text) => {
  let newItem = document.createElement('li');
  newItem.classList.add('list-group-item', 'game-option');
  newItem.innerHTML = text;
  document.getElementById('summary_list').append(newItem);
};
const getFormInputValue = (formId) => {
  console.log(document.getElementById('id_form-' + formId + '-option').value);
  return document.getElementById('id_form-' + formId + '-option').value;
};

const onAddClick = () => {
  const formCount = document.getElementById('id_form-TOTAL_FORMS').value;
  if (!getFormInputValue(formCount - 1)) return;
  const newForm = document.getElementById('empty_form').innerHTML.replace(/__prefix__/g, formCount);
  document.getElementById('game_options').innerHTML += newForm;
  document.getElementById('id_form-TOTAL_FORMS').value = (parseInt(formCount) + 1);
  const text = document.getElementById('id_form-' + (formCount - 1) + '-option').value;
  if (text) {
    // addOption(text);
    addSummaryItem(text);
  }
};

const updateSummaryTitle = () => {
  let newTitle = document.querySelector("input#option").value;
  console.log(newTitle);
  document.getElementById('summary_title').innerHTML = newTitle;
};

const submit = () => {

};


document.getElementById('add_option').addEventListener('click', onAddClick);
document.querySelector("input#option").addEventListener('change', updateSummaryTitle);
document.querySelector("input#option").addEventListener('input', updateSummaryTitle);
document.querySelector('input#is_bool').addEventListener('click', () => {
  if (document.querySelector('input#is_bool').checked) {
    document.getElementById('option_choices').classList.add("d-none");
  } else {
    document.getElementById('option_choices').classList.remove("d-none");
  }
});
