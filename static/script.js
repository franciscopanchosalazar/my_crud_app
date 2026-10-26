// CREATE
    document.getElementById("serviceForm").addEventListener("submit", async function(e) {
      e.preventDefault(); //Avoids the page from reloading
      const formData = new FormData(this); //Collects the form data, 'this' refers to the form itself.
      const jsonData = Object.fromEntries(formData.entries()); //entries() gives us key/value pairs and Object.fromEntries converts them into a js object.

      //await waits until the server replies before moving on.
      //fetch makes a network request to the Flask backend.
      //POST says we are adding data
      //Content-type says we are sending Json
      //stringify converts Json into text 
      const response = await fetch("http://127.0.0.1:5000/add_service", {
        method: "POST", 
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(jsonData)
      });

      const result = await response.json();
      alert(JSON.stringify(result));

      loadServices(); // refresh table
    });

    // READ
    async function loadServices() {
      const response = await fetch("http://127.0.0.1:5000/get_services");
      const services = await response.json();

const table = document.getElementById("servicesTable");
table.innerHTML = `
  <thead>
    <tr>
      <th>ID</th><th>Type</th><th>Brand</th><th>Model</th>
      <th>SN</th><th>Issue</th><th>Date</th><th>Technician</th>
      <th>Status</th><th>Actions</th>
    </tr>
  </thead>
  <tbody></tbody>`;

const tbody = table.querySelector("tbody");
services.forEach(s => {
  tbody.innerHTML += `
    <tr>
      <td>${s.id}</td>
      <td>${s.equipment_type}</td>
      <td>${s.brand}</td>
      <td>${s.model}</td>
      <td>${s.serial_number}</td>
      <td>${s.issue_reported}</td>
      <td>${s.service_date}</td>
      <td>${s.technician}</td>
      <td>${s.status}</td>
      <td>
        <button onclick="updateService(${s.id}, 'Pending')">Pending</button>
        <button onclick="updateService(${s.id}, 'In Progress')">In Progress</button>
        <button onclick="updateService(${s.id}, 'Completed')">Completed</button>
        <button onclick="deleteService(${s.id})">Delete</button>
      </td>
    </tr>`;
});
    }

    // UPDATE
    async function updateService(id, newStatus) {
    const response = await fetch(`http://127.0.0.1:5000/services/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus })
    });
    const result = await response.json();
    alert(JSON.stringify(result));
    loadServices(); // refresh table
    }

    // DELETE
    async function deleteService(id) {
      const response = await fetch(`http://127.0.0.1:5000/services/${id}`, {
        method: "DELETE"
      });
      const result = await response.json();
      alert(JSON.stringify(result));
      loadServices();
    }
    