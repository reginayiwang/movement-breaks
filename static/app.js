const $startButton = $('#start-button');
const $resetButton = $('#reset-button');
const $timerDisplay = $('#timer');

let secLeft;
let interval;

function startTimer() {
    secLeft = 3600;
    interval = setInterval(countDown, 1000);
}

function countDown() {
    secLeft--;
    displayTime(secLeft)
    
    if (secLeft === 0) {
        clearInterval(interval)
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
    secLeft = 3600;
    displayTime(secLeft);
    clearInterval(interval);
}

$startButton.on('click', startTimer);
$resetButton.on('click', resetTimer)