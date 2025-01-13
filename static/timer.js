const $startButton = $('#start-button');
const $resetButton = $('#reset-button');
const $nextButton = $('#next-button')
const $timerDisplay = $('#timer');
const $exerciseCont = $('.exercise-container')
const $exerciseName = $('#exercise-name');
const $exerciseImg = $('#exercise-img');
const $instructions = $('#exercise-instructions');

let secLeft;
let interval;
let exercises;
let exerciseIdx = 0;

function startTimer() {
    $(this).prop('disabled', true);
    secLeft = 5;
    displayTime(secLeft)
    interval = setInterval(countDown, 1000);
}

function countDown() {
    secLeft--;
    console.log(secLeft)
    displayTime(secLeft)
    
    if (secLeft === 0) {
        clearInterval(interval)
        startExerciseBreak()
    }
}

function displayTime(time) {
    $timerDisplay.text(formatTime(time));
}

function formatTime(seconds) {
    hours = Math.floor(seconds / 3600);
    mins = Math.floor((seconds % 3600) / 60);
    secs = seconds % 60; 

    return (hours ? `${hours}:` : '') + (mins >= 10 ? `${mins}:` : `0${mins}:`) +  (secs >= 10 ? `${secs}` : `0${secs}`); 
}

function resetTimer() {
    $exerciseCont.hide();
    $startButton.prop('disabled', false);
    secLeft = 5;
    displayTime(secLeft);
    clearInterval(interval);
}

async function startExerciseBreak() {
    console.log("start break")
    try {
        res = await axios.get('./exercises');
        exercises = _.shuffle(res.data);
        console.log(exercises)
        exerciseIdx = 0;
        showNextExercise();
    } catch (e) {
        // TO DO: Add error messaging to page
        console.log(e);
    }
}

function showNextExercise() {
    console.log("show next")
    exercise = exercises[exerciseIdx % exercises.length];
    $exerciseImg.attr('src', exercise['gifUrl']);
    $exerciseImg.attr('alt', exercise['name']);
    $exerciseName.text(exercise['name']);
    $instructions.empty();
    for (let ins of exercise['instructions']) {
        $instructions.append($(`<li>${ins}</li>`));
    }
    $exerciseCont.show();
    exerciseIdx++;
}

$startButton.on('click', startTimer);
$resetButton.on('click', resetTimer);
$nextButton.on('click', showNextExercise);