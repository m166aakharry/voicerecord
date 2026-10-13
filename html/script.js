let recorder = null;
let audioChunks = [];
let audioPlayer = document.getElementById("audioPlayer");
let startButton = document.getElementById("startButton");
let stopButton = document.getElementById("stopButton");
let recordings = document.getElementById("recordings");

startButton.addEventListener(
    "click",
    async () => {
        audioChunks = [];
        let audioStream = await navigator.mediaDevices.getUserMedia({
    		                audio: true
        	            }
        );
	recorder = new MediaRecorder(audioStream);
	recorder.addEventListener(
    		"dataavailable",
    		(event) => {
    			audioChunks.push(event.data);
    		}
    	)
    	recorder.start();
    	}
);

stopButton.addEventListener(
	"click",
	() =>{ 
		recorder.addEventListener(
    		"stop",
    		() => {
    			let audioBlob = new Blob(audioChunks,
    					            {
    								    type : "audio/webm"
    							    }   
    						    );               
                let formData = new FormData;
				let filename = `recording_${Date.now()}.webm`
				formData.append("audio", audioBlob, filename);
				audioPlayer.addEventListener(
					"loadedmetadata",
					async () => {
						formData.append("duration", audioPlayer.duration);
						let response = await fetch("/api/upload", {
    										method: "POST",
											body: formData
											});
						let result = await response.json();
						await loadRecordings()
					},
					{once: true}
				)
				let audioURL = URL.createObjectURL(audioBlob);
				audioPlayer.src = audioURL;

    		}
		);
		recorder.stop();		
	}
);

async function loadRecordings() {
	recordings.innerHTML = "";
	console.log("loadRecordings");
	let response = await fetch("/api/recordings");
	let result = await response.json();
	for (let record of result) {
		let item = document.createElement("div");
		item.style.marginBottom = "10px";
		item.append(record.created_at);
		let audio = document.createElement("audio");
		audio.style.display = "block";
		audio.controls = true;
		audio.src = `/api/audio/${record.filename}`
		item.append(audio);
		let deletebutton = document.createElement("button")
		deletebutton.append("刪除")
		deletebutton.addEventListener(
			"click",
			async () =>{
				let response = await fetch(`/api/recordings/${record.id}`, {
									method: "DELETE",
								});
				if (response.ok){
					item.remove();
				}
			}
		)
		item.append(deletebutton);
		recordings.append(item);
	}
}
loadRecordings();
