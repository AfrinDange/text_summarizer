const express = require('express');
const path = require('path');
const {spawnSync, spawn} = require('child_process');
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
    const summarizer = spawnSync('python', ['summarizer.py', req.body.text]);

    if(summarizer.status == 0) {
        const dataToSend = summarizer.stdout.toString();
        if(summarizer.stderr.toString() != "") console.error("ERROR in Summary Process: ", summarizer.stderr.toString());
        console.log("Summary Process exited with code 0");
        res.render('summary.html', {text: req.body.text, summary: dataToSend});
    } else {
        res.send("ERROR! TRY AGAIN!");
    }
})

app.get('/evaluate-model', (req, res) => {
    res.render('model_eval.html', {metrics: null});
})

app.post('/evaluation-results', (req, res) => {
    //generate summary        
    const summarizer = spawnSync('python', ['summarizer.py', req.body.text]);
    if(summarizer.stderr.toString() != "") console.error("ERROR in Summary Process: ..", summarizer.stderr.toString(), "..");
    if(summarizer.status == 0) {
        const computer_summ = summarizer.stdout.toString();
        

        //evaluate model
        const model_eval = spawnSync('python', ['model_eval.py', req.body.human_summ, computer_summ]);
        if(model_eval.stderr.toString() != "") console.error("ERROR in Evaluation Process: ", model_eval.stderr.toString());
        if(model_eval.status == 0) {
            const metrics = JSON.parse(model_eval.stdout.toString());
            console.log("Evaluation process exited with code 0");
            res.render('model_eval.html', {metrics: metrics});
        } else {
            res.send("ERROR! TRY AGAIN!");
        }
    } 
})

app.get("*", (req, res) => {
    res.send("404 ERROR. PAGE NOT FOUND!")
})

app.listen(port, () => console.log(`App listening on port ${port}!`));