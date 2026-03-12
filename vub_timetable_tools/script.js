let selectedCells = new Array();
let interval = 50
let timeArray = [
    [8, 0],
    [9, 0],
    [10, 10],
    [11, 10],
    [12, 10],
    [13, 20],
    [14, 20],
    [15, 30],
    [16, 30],
    [17, 30],
    [18, 30],
    [19, 30],
    [20, 30]
];



function updateAllTimeCells() {
    for (let i=0; i<timeArray.length; i++) {
        const timeCell = document.getElementById('t' + (i+1));
        if (!timeCell) continue;
        const start = timeArray[i];
        const end = timeAdd(start[0], start[1], 0, interval);
        timeCell.innerHTML = `${i+1} <button title='開頭 + 10 分鐘'>▲</button><button title='開頭 - 10 分鐘'>▼</button>${prefixZero(start[0])}:${prefixZero(start[1])} ~ ${prefixZero(end[0])}:${prefixZero(end[1])}`;
    }
}


window.onload = function() {
    const table = document.getElementById('timetable').getElementsByTagName('tbody')[0];
    
    document.getElementById('interval').onchange = function() {
        interval = Number(this.value);
        updateAllTimeCells();
        bindTimeCellButtons();
    };
    
    updateAllTimeCells();
    bindTimeCellButtons();
    
    
    
    for (let i=0; i<table.rows.length; i++) {
        for (let j=1; j<table.rows[i].cells.length; j++) {
            const cell = table.rows[i].cells[j];
            cell.style.cursor = 'pointer';
            cell.onclick = function() {
                const cellIndex = selectedCells.findIndex(arr => arr[0] === j && arr[1] === i + 1);
                if (cellIndex !== -1) {
                    selectedCells.splice(cellIndex, 1);
                    cell.classList.remove('selected');
                } else {
                    selectedCells.push([j, i + 1]);
                    cell.classList.add('selected');
                }
            };
        }
    }
};


// ▲▼ Buttons
function bindTimeCellButtons() {
    for (let i=0; i<timeArray.length; i++) {
        const timeCell = document.getElementById('t' + (i + 1));
        if (!timeCell) continue;
        const buttons = timeCell.querySelectorAll('button');
        if (buttons.length < 2) continue;
        buttons[0].onclick = function(e) {
            e.stopPropagation();
            // ▲ -10 mins
            timeArray[i] = timeAdd(timeArray[i][0], timeArray[i][1], 0, -10);
            updateAllTimeCells();
            bindTimeCellButtons();
        };
        buttons[1].onclick = function(e) {
            e.stopPropagation();
            // ▼ +10 mins
            timeArray[i] = timeAdd(timeArray[i][0], timeArray[i][1], 0, 10);
            updateAllTimeCells();
            bindTimeCellButtons();
        };
    }
}


function timeAdd(hour, minute, addHour, addMinute) {
    let totalMinutes = hour * 60 + minute + addHour * 60 + addMinute;
    totalMinutes = ((totalMinutes % 1440) + 1440) % 1440;
    let newHour = Math.floor(totalMinutes / 60);
    let newMinute = totalMinutes % 60;
    return [newHour, newMinute];
}


function prefixZero(number) {
    return number < 10 ? '0' + number : number.toString();
}


function addCourse() {
    const name = document.getElementById("courseName").value.trim();
    const instructor = document.getElementById("courseInstructor").value.trim();
    const location = document.getElementById("courseLocation").value.trim();

    if (!name) {
        alert("請輸入課程名稱");
        return;
    }

    const table = document.getElementById('timetable').getElementsByTagName('tbody')[0];
    for (let i=0; i<selectedCells.length; i++) {
        let row = table.rows[selectedCells[i][1]-1]; 
        let cell = row.cells[selectedCells[i][0]];
        cell.textContent = `${name}\n${instructor?instructor:'-'}\n${location?location:'-'}`;
        cell.classList.remove('selected');
    }
    selectedCells = new Array();
}


function clearSelected() {
    alert("你確定嗎?");
    const table = document.getElementById('timetable').getElementsByTagName('tbody')[0];
    for (let i=0; i<selectedCells.length; i++) {
        let row = table.rows[selectedCells[i][1]-1]; 
        let cell = row.cells[selectedCells[i][0]];
        cell.textContent = "";
        cell.classList.remove('selected');
    }
    selectedCells = new Array();
}


function exportToJson() {
    const table = document.getElementById('timetable').getElementsByTagName('tbody')[0];
    let cols = table.rows[0].cells.length - 1;
    let rows = table.rows.length;
    let cells = [];

    for (let j = 1; j <= cols; j++) {
        let colData = [];
        for (let i = 0; i < rows; i++) {
            colData.push(table.rows[i].cells[j].textContent);
        }
        cells.push(colData);
    }

    const data = {
        timeArray: timeArray,
        interval: interval,
        cells: cells // [column][row]
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], {type: "application/json"});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = "timetable.json";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}