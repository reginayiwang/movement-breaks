const $startButton = $('#start-button');
const $resetButton = $('#reset-button');
const $nextButton = $('#next-button')
const $blockButton = $('#block-button')
const $timerDisplay = $('#timer');
const $exerciseCont = $('.exercise-container')
const $exerciseName = $('#exercise-name');
const $exerciseImg = $('#exercise-img');
const $instructions = $('#exercise-instructions');
const $alert = $('.alert');
const $header = $('h1')

let secLeft;
let interval;
let exercises;
let currExerciseId;
let exerciseIdx = 0;
let workPhase = true;

/**
 * Start timer count down 
 */
function startTimer() {
    $(this).prop('disabled', true); 

    // Set time in seconds based on whether it is a work phase or break phase
    secLeft = (workPhase ? workMins : breakMins) * 60;

    // Uncomment for quicker testing
    // secLeft = 5
    interval = setInterval(countDown, 1000);
}

/**
 * Handle timer count down, switching phases when hitting 0.
 */
function countDown() {
    secLeft--;
    $timerDisplay.text(formatTime(secLeft));
    
    if (secLeft === 0) {
        clearInterval(interval);
        playSound();
        workPhase = !workPhase;
        if (!workPhase) {
            startExerciseBreak();
        }
    }
}

/**
 * Play alarm sound
 */
function playSound() {
    let ding = new Audio('https://cdn.freesound.org/previews/22/22627_7037-lq.mp3');
    ding.play();
}

/**
 * Return string converting seconds into HH:MM:SS format
 */
function formatTime(seconds) {
    hours = Math.floor(seconds / 3600);
    mins = Math.floor((seconds % 3600) / 60);
    secs = seconds % 60; 

    return (hours ? `${hours}:` : '') + (mins >= 10 ? `${mins}:` : `0${mins}:`) +  (secs >= 10 ? `${secs}` : `0${secs}`); 
}

/**
 * Reset timer to work phase
 */
function resetTimer() {
    $exerciseCont.hide();
    $startButton.prop('disabled', false);
    $timerDisplay.text(formatTime(workMins * 60));
    $header.text("Let's get to work!")
    clearInterval(interval);
}

/**
 * Start exercise phase
 */
async function startExerciseBreak() {
    startTimer();
    $header.text('Get up and take a break!')
    exerciseIdx = 0;
    exercises = await fetchExercises();
    if (exercises) {
        showNextExercise();
    } 
}

/**
 * Return exercises fetched from database
 * Show alerts if exercises were not found for current settings, or for error retrieving exercises
 */
async function fetchExercises() {
    try {
        res = await axios.get('./exercises');
        if (!res.data.exercises_found) {
            showAlert('warning', 'No exercises found for current equipment/target settings. Please try adjusting your selections. Displaying default bodyweight exercises.')
        }
        return _.shuffle(res.data.exercises);
    } catch (e) {
        showAlert('danger', 'Could not retrieve exercises.')
        console.error(e);
    }
}

/**
 * Display next exercise in exercises lsit
 */
function showNextExercise() {
    exercise = exercises[exerciseIdx % exercises.length];
    currExerciseId = exercise['id']
    $exerciseImg.attr('src', exercise['gifUrl']);
    $exerciseImg.attr('alt', exercise['name']);
    $exerciseName.text(exercise['name']);
    $instructions.empty();
    for (let ins of exercise['instructions']) {
        $instructions.append($(`<li class="list-group-item">${ins}</li>`));
    }
    $exerciseCont.show();
    exerciseIdx++;
}

/**
 * Display alert styled for given type with given message
 */
function showAlert(type, message) {
    $alert.attr("class", `alert alert-${type} alert-dismissable fade show`);
    $alert.find('#alert-message').text(message);
    $alert.show()
}

/**
 * Block current exercise
 * Blocked exercises will not show up in future exercise breaks unless no exercises are found for current settings
 */
async function blockExercise() {
    try {
        res = await axios.post(`./users/${userId}/block`, {exercise_id: currExerciseId});
        if (res.status === 201) {
            exerciseIdx--;
            exercises.splice(exerciseIdx, 1);

            // Fetch new exercises (will default to bodyweight exercises) if blocking leads to no exercises left
            if (exercises.length === 0) {
                exerciseIdx = 0;
                exercises = await fetchExercises();
            }

            showNextExercise();
        } else {
            showAlert('danger', 'Unauthorized to block exercise.')
        }
    } catch (e) {
        showAlert('danger', 'Could not block exercise.')
        console.error(e);
    }
}

$startButton.on('click', startTimer);
$resetButton.on('click', resetTimer);
$blockButton.on('click', blockExercise);
$nextButton.on('click', showNextExercise);
$( document ).ready(() => {
    if (!userId) {
        $blockButton.hide();
    }
    $alert.hide();
    $timerDisplay.text(formatTime(workMins * 60));
});