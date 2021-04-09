const express = require('express');
const path = require('path');
const {spawn} = require('child_process');
const app = express();
const port = 3000

app.use(express.urlencoded({extended : true}));
app.use(express.json());

app.set('views', path.join(__dirname, '/views'));
app.engine('html', require('ejs').renderFile);
app.set('view engine', 'ejs');
app.use( express.static( "public" ) );

app.get('/', (req, res) => {
    res.render('index.html');
})

app.post('/get-summary', (req,res) => {
    //child process to call the python script
    const summarizer = spawn('python', 
            ['summarizer.py', req.body.text]);

    summarizer.stdout.on('data', (data) => {
        dataToSend = data.toString();
    })

    summarizer.stderr.on('data', (data) => {
        console.log('stderr: ' + data.toString());
    })

    summarizer.on('close', (code) => {
        console.log(`Summary process closed all stdio with code ${code}`);
        res.render('summary.html', {text: req.body.text, summary: dataToSend});
        //res.send("Original text: " + req.body.text + "\nSummary: " + dataToSend);
    })
})

app.get('/evaluate-model', (req, res) => {
    res.render('model_eval.html', {scores: ""});
})

app.post('/evaluate-model', (req, res) => {
    //generate summary
    var computer_summ;

    
    console.log("Original text: " + req.body.text);
    const summarizer = spawn('python', ['summarizer.py', req.body.text]);

    summarizer.stdout.on('data', (data) => {
        computer_summ = data.toString();
    })

    
    summarizer.stderr.on('data', (data) => {
        console.log('stderr: ' + data.toString());
    })
    
    summarizer.on('close', (code) => {
        console.log(`Summary process closed all stdio with code ${code}`);
    })

    //evaluate model
    console.log("human summary: " + req.body.human_summ + "\n\n\nComputer SUmmary: " + computer_summ);
    
    const model_eval = spawn('python', ['model_eval.py', req.body.human_summ, computer_summ]);


    model_eval.stdout.on('data', (data) => {
        scores = data.toString();
    })

    model_eval.stderr.on('data', (data) => {
        console.log('stderr: ' + data.toString());
    })

    model_eval.on('close', (code) => {
        console.log(`Evaluation process closed all stdio with code ${code}`);
        console.log(scores);
        res.render('model_eval.html', {scores: scores});
    })
})

app.listen(port, () => console.log(`Example app listening on port ${port}!`));