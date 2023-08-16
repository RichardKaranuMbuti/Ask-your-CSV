// custom_script.js

document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM content loaded.");
    
    // Function to load rooms from API
    function loadRooms() {
        console.log("Loading rooms...");
        fetch("http://miksi.pythonanywhere.com/room_list/?user_id=v1fY11z4w3C07&company_name=Miksi")
            .then(response => response.json())
            .then(data => {
                console.log("Data received:", data);
                const sidebar = document.querySelector(".sidebar");
                
                // Clear existing content
                sidebar.innerHTML = "";
                
                // Create buttons for each room
                data.room_names.forEach(roomName => {
                    const roomButton = document.createElement("button");
                    roomButton.className = "btn btn-light btn-block mb-2 room-button";
                    roomButton.textContent = roomName;
                    
                    // Create icons for rename and delete
                    const renameIcon = document.createElement("i");
                    renameIcon.className = "fas fa-edit";
                    const deleteIcon = document.createElement("i");
                    deleteIcon.className = "fas fa-trash";
                    
                    // Append icons to the room button
                    roomButton.appendChild(renameIcon);
                    roomButton.appendChild(deleteIcon);
                    
                    sidebar.appendChild(roomButton);
                });
            })
            .catch(error => {
                console.error("Error loading rooms:", error);
            });
    }
    
    // Load rooms when the "Load Rooms" button is clicked
    const loadRoomsButton = document.getElementById("load-rooms-button");
    loadRoomsButton.addEventListener("click", loadRooms);
    console.log("Load rooms button listener added.");
});
