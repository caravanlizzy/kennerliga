const getData = () => {
    const dataUrl = 'https://boardgamearena.com/table?table=308496085';
    fetch(
        dataUrl,
        {
            headers: {
                'Access-Control-Allow-Origin':'*'
            }
        }).then(result => console.log(result));
};

getData();

// ANNOTATION: has to be moved to python
