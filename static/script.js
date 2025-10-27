const allSideMenu = document.querySelectorAll('#sidebar .side-menu.top li a');

allSideMenu.forEach(item=> {
	const li = item.parentElement;

	item.addEventListener('click', function () {
		allSideMenu.forEach(i=> {
			i.parentElement.classList.remove('active');
		})
		li.classList.add('active');
	})
});




// TOGGLE SIDEBAR
const menuBar = document.querySelector('#content nav .bx.bx-menu');
const sidebar = document.getElementById('sidebar');

menuBar.addEventListener('click', function () {
	sidebar.classList.toggle('hide');
})







const searchButton = document.querySelector('#content nav form .form-input button');
const searchButtonIcon = document.querySelector('#content nav form .form-input button .bx');
const searchForm = document.querySelector('#content nav form');

searchButton.addEventListener('click', function (e) {
	if(window.innerWidth < 576) {
		e.preventDefault();
		searchForm.classList.toggle('show');
		if(searchForm.classList.contains('show')) {
			searchButtonIcon.classList.replace('bx-search', 'bx-x');
		} else {
			searchButtonIcon.classList.replace('bx-x', 'bx-search');
		}
	}
})





if(window.innerWidth < 768) {
	sidebar.classList.add('hide');
} else if(window.innerWidth > 576) {
	searchButtonIcon.classList.replace('bx-x', 'bx-search');
	searchForm.classList.remove('show');
}


window.addEventListener('resize', function () {
	if(this.innerWidth > 576) {
		searchButtonIcon.classList.replace('bx-x', 'bx-search');
		searchForm.classList.remove('show');
	}
})



const switchMode = document.getElementById('switch-mode');

switchMode.addEventListener('change', function () {
	if(this.checked) {
		document.body.classList.add('dark');
	} else {
		document.body.classList.remove('dark');
	}
})
// Update the weather display with the current weather for a specific location
function updateWeather(location) {
    const apiKey = '0b22233dd9e00aabfdf9941febafcfa3'; // Replace 'YOUR_API_KEY' with your actual API key
    const url = https://api.openweathermap.org/data/2.5/weather?q=${location}&appid=${apiKey};

    fetch(url)
        .then(response => response.json())
        .then(data => {
            const weatherText = document.getElementById('weather-text');
            if (weatherText) {
                const weatherDescription = data.weather[0].description;
                weatherText.innerHTML = `
                    <h3>${weatherDescription}</h3>
                    <p>Weather</p>
                `;
            }
        })
        .catch(error => console.error('Error fetching weather data:', error));
}

// Call the updateWeather function with the location (e.g., Karnataka) when the page loads
window.addEventListener('load', function () {
    updateWeather('karnataka');
});

function updateDetectionInfo() {
	fetch('/detect_accident')
		.then(response => response.text())
		.then(data => {
			document.getElementById('detection_info').innerText = data;
		});
}

setInterval(updateDetectionInfo, 1000);