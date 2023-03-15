const addOption = (text) => {
  let newItem = document.createElement('div');
  newItem.classList.add('p-2');
  newItem.innerHTML = '- ' + text;
  document.getElementById('game_options').append(newItem);
};

const addSummaryItem = (text) => {
  let newItem = document.createElement('li');
  newItem.classList.add('list-group-item', 'game-option');
  newItem.innerHTML = text;
  document.getElementById('summary_list').append(newItem);
};

const onAddClick = () => {
  let inputField = document.getElementById('option_input');
  const text = inputField.value;
  addOption(text);
  addSummaryItem(text);
  inputField.value = "";
};

const updateSummaryTitle = () => {
  let newTitle = document.querySelector("input#name").value;
  console.log(newTitle);
  document.getElementById('summary_title').innerHTML = newTitle;
};

const submit = () => {

};

document.getElementById('add_option').addEventListener('click', onAddClick);
document.querySelector("input#name").addEventListener('change', updateSummaryTitle);
document.querySelector("input#name").addEventListener('input', updateSummaryTitle);

