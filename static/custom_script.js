document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM content loaded.");

    // Load messages for a specific room
    function loadMessages(roomId) {
        fetch(`https://miksi.pythonanywhere.com/room_messages/?user_id=v1fY11z4w3C07&room_id=${roomId}`)
            .then(response => response.json())
            .then(data => {
                const chatMessagesBox = document.querySelector(".chat-messages-box");
                chatMessagesBox.innerHTML = ""; // Clear existing messages
                
                let prevAgentResponse = null; // Keep track of previous agent_response
                
                // Iterate through messages to display in message-like structure
                data.Messages.forEach(message => {
                    const messageContainer = document.createElement("div");
                    messageContainer.className = `message-container ${message.agent_response ? "agent-response" : ""}`;

                    const messageContent = document.createElement("div");
                    messageContent.className = "message-content";
                    messageContent.textContent = message.content;

                    messageContainer.appendChild(messageContent);
                    chatMessagesBox.appendChild(messageContainer);
                    
                    // Add margin between agent_response changes
                    if (prevAgentResponse !== null && prevAgentResponse !== message.agent_response) {
                        const marginElement = document.createElement("div");
                        marginElement.className = "message-margin";
                        chatMessagesBox.appendChild(marginElement);
                    }
                    
                    prevAgentResponse = message.agent_response;
                });
            })
            .catch(error => {
                console.error("Error loading messages:", error);
            });
    }

    // Load rooms and messages immediately when the page loads
    function initialize() {
        loadRooms();
        loadMessages("8W392R2k"); // Replace with the appropriate room_id
    }

    // Call initialize function when the page loads
    initialize();

    // Function to load rooms from API
    function loadRooms() {
        console.log("Loading rooms...");
        fetch("https://miksi.pythonanywhere.com/room_list/?user_id=v1fY11z4w3C07&company_name=Miksi")
            .then(response => response.json())
            .then(data => {
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

                    // Add click event to load messages for the room
                    roomButton.addEventListener("click", function () {
                        loadMessages(roomName);
                    });
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
