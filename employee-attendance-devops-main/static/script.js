
const API = "";

const employeeForm = document.getElementById("employeeForm");
const attendanceForm = document.getElementById("attendanceForm");

const today = new Date();
const todayString = [
    today.getFullYear(),
    String(today.getMonth() + 1).padStart(2, "0"),
    String(today.getDate()).padStart(2, "0")
].join("-");

document.getElementById("currentDate").textContent =
    today.toLocaleDateString("en-IN", {
        day: "numeric",
        month: "short",
        year: "numeric"
    });

document.getElementById("attendanceDate").value = todayString;

function showMessage(message, isError = false) {
    const box = document.getElementById("message");

    box.textContent = message;
    box.className = isError ? "message error" : "message";
    box.style.display = "block";

    setTimeout(() => {
        box.style.display = "none";
    }, 3000);
}

async function apiRequest(url, options = {}) {
    const response = await fetch(API + url, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...options.headers
        }
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error || "Something went wrong");
    }

    return data;
}

function createCell(text) {
    const cell = document.createElement("td");
    cell.textContent = text ?? "";
    return cell;
}

async function loadDashboard() {
    try {
        const [employees, records] = await Promise.all([
            apiRequest("/api/employees"),
            apiRequest("/api/attendance")
        ]);

        renderEmployees(employees);
        renderAttendance(records);
        updateStatistics(employees, records);

    } catch (error) {
        showMessage(error.message, true);
    }
}

function renderEmployees(employees) {
    const select = document.getElementById("attendanceEmployee");

    select.replaceChildren();

    const defaultOption = document.createElement("option");
    defaultOption.value = "";
    defaultOption.textContent = "Choose employee";
    select.appendChild(defaultOption);

    employees.forEach(employee => {
        const option = document.createElement("option");
        option.value = employee.id;
        option.textContent = `${employee.name} - ${employee.department}`;
        select.appendChild(option);
    });
}

function renderAttendance(records) {
    const table = document.getElementById("attendanceTable");
    table.replaceChildren();

    if (records.length === 0) {
        const row = document.createElement("tr");
        const cell = document.createElement("td");

        cell.colSpan = 4;
        cell.className = "empty-state";
        cell.textContent = "No attendance records available.";

        row.appendChild(cell);
        table.appendChild(row);
        return;
    }

    records.forEach(record => {
        const row = document.createElement("tr");

        row.appendChild(createCell(record.name));
        row.appendChild(createCell(record.department));
        row.appendChild(createCell(record.attendance_date));

        const statusCell = document.createElement("td");
        const badge = document.createElement("span");

        badge.className = `status ${record.status}`;
        badge.textContent = record.status;

        statusCell.appendChild(badge);
        row.appendChild(statusCell);

        table.appendChild(row);
    });
}

function updateStatistics(employees, records) {
    const todayRecords = records.filter(record =>
        String(record.attendance_date).slice(0, 10) === todayString
    );

    const present = todayRecords.filter(
        record => record.status === "Present"
    ).length;

    const absent = todayRecords.filter(
        record => record.status === "Absent"
    ).length;

    const rate = todayRecords.length
        ? Math.round((present / todayRecords.length) * 100)
        : 0;

    document.getElementById("totalEmployees").textContent =
        employees.length;

    document.getElementById("presentCount").textContent =
        present;

    document.getElementById("absentCount").textContent =
        absent;

    document.getElementById("attendanceRate").textContent =
        rate + "%";
}

employeeForm.addEventListener("submit", async event => {
    event.preventDefault();

    const employee = {
        name: document.getElementById("employeeName").value.trim(),
        email: document.getElementById("employeeEmail").value.trim(),
        department: document.getElementById("employeeDepartment").value.trim()
    };

    try {
        await apiRequest("/api/employees", {
            method: "POST",
            body: JSON.stringify(employee)
        });

        employeeForm.reset();
        showMessage("Employee added successfully!");

        await loadDashboard();

    } catch (error) {
        showMessage(error.message, true);
    }
});

attendanceForm.addEventListener("submit", async event => {
    event.preventDefault();

    const attendance = {
        employee_id: Number(
            document.getElementById("attendanceEmployee").value
        ),
        attendance_date:
            document.getElementById("attendanceDate").value,
        status:
            document.getElementById("attendanceStatus").value
    };

    try {
        await apiRequest("/api/attendance", {
            method: "POST",
            body: JSON.stringify(attendance)
        });

        showMessage("Attendance saved successfully!");

        await loadDashboard();

    } catch (error) {
        showMessage(error.message, true);
    }
});

loadDashboard();
