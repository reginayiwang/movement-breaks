const $startButton = $('#start-button');
const $resetButton = $('#reset-button');
const $nextButton = $('#next-button')
const $timerDisplay = $('#timer');
const $exerciseCont = $('.exercise-container')
const $exerciseName = $('#exercise-name');
const $exerciseImg = $('#exercise-img');
const $instructions = $('#exercise-instructions');
const $alert = $('.alert');

let secLeft;
let interval;
let exercises;
let exerciseIdx = 0;
let workPhase = true;

function startTimer() {
    $(this).prop('disabled', true); 
    secLeft = (workPhase ? workMins : breakMins) * 60;

    // Uncomment for quicker testing
    // secLeft = 5
    interval = setInterval(countDown, 1000);
}

function countDown() {
    secLeft--;
    displayTime(secLeft);
    
    if (secLeft === 0) {
        clearInterval(interval);
        workPhase = !workPhase;
        if (!workPhase) {
            startExerciseBreak();
        }
    }
}

function displayTime(seconds) {
    $timerDisplay.text(formatTime(seconds));
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
    displayTime(workMins * 60);
    clearInterval(interval);
}

async function startExerciseBreak() {
    startTimer();
    try {
        res = await axios.get('./exercises');
        exercises = _.shuffle(res.data.exercises);
        if (!res.data.exercises_found) {
            showAlert('warning', 'No exercises found for current equipment/target settings. Please try adjusting your selections. Displaying default bodyweight exercises.')
        }
        exerciseIdx = 0;
        showNextExercise();
    } catch (e) {
        showAlert('danger', 'Could not retrieve exercises.')
        console.error(e);
    }
}

function showNextExercise() {
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

function showAlert(type, message) {
    $alert.attr("class", `alert alert-${type}`);
    $alert.text(message);
    $alert.show()
}

$startButton.on('click', startTimer);
$resetButton.on('click', resetTimer);
$nextButton.on('click', showNextExercise);
$( document ).ready(() => {
    $alert.hide();
    displayTime(workMins * 60);
});