// bookingsView.js
import { mockService } from '../mocks/mockService.js';
import { showToast, openModal, closeModal } from '../app.js';

let activeResource = 'Boardroom Alfa (Floor 2)';
let activeDate = '2026-07-13'; // Simulating a target date
let listenersBound = false;

export const bookingsView = {
  async init() {
    try {
      // 1. Render Calendar Grid Layout
      await renderCalendar();

      // 2. Bind listeners
      registerListeners();
    } catch (err) {
      console.error('Error rendering bookings view:', err);
    }
  }
};

function registerListeners() {
  if (listenersBound) return;

  // Resource buttons selection clicks
  const sidebar = document.getElementById('resource-list');
  if (sidebar) {
    sidebar.addEventListener('click', (e) => {
      const btn = e.target.closest('.resource-btn');
      if (btn) {
        document.querySelectorAll('.resource-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        activeResource = btn.getAttribute('data-resource');
        renderCalendar();
      }
    });
  }

  // Date picker selection changes
  const dateInput = document.getElementById('calendar-date-selector');
  if (dateInput) {
    dateInput.addEventListener('change', (e) => {
      activeDate = e.target.value;
      renderCalendar();
    });
  }

  // Launch Reserve Resource Modal button
  const bookBtn = document.getElementById('btn-open-book-modal');
  if (bookBtn) {
    bookBtn.addEventListener('click', () => {
      // Prefill values in form
      document.getElementById('form-book-resource-name').value = activeResource;
      document.getElementById('form-book-date').value = activeDate;
      openModal('modal-resource-booking');
    });
  }

  // Handle Booking Form Submit
  const bookingForm = document.getElementById('form-resource-booking');
  if (bookingForm) {
    bookingForm.addEventListener('submit', handleBookingSubmit);
  }

  listenersBound = true;
}

async function renderCalendar() {
  const container = document.getElementById('calendar-grid-body');
  if (!container) return;

  // Set selected date text label
  const dateLabel = document.getElementById('calendar-date-display');
  if (dateLabel) {
    dateLabel.textContent = new Date(activeDate).toLocaleDateString(undefined, {
      weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
    });
  }

  const dateInput = document.getElementById('calendar-date-selector');
  if (dateInput) {
    dateInput.value = activeDate;
  }

  const bookings = await mockService.getBookings();
  const dayBookings = bookings.filter(b => 
    b.resource_name === activeResource && 
    b.booking_date === activeDate &&
    b.status === 'Confirmed'
  );

  // Core operating hours slots (08:00 - 18:00 in 2-hour increments)
  const timeSlots = [
    { start: '08:00', end: '10:00', label: '08:00 - 10:00' },
    { start: '10:00', end: '12:00', label: '10:00 - 12:00' },
    { start: '12:00', end: '14:00', label: '12:00 - 14:00' },
    { start: '14:00', end: '16:00', label: '14:00 - 16:00' },
    { start: '16:00', end: '18:00', label: '16:00 - 18:00' }
  ];

  let gridHtml = '';

  timeSlots.forEach(slot => {
    // Check if there is a booking that overlaps this timeslot
    const matchingBooking = dayBookings.find(b => {
      return !(slot.end <= b.start_time || slot.start >= b.end_time);
    });

    gridHtml += `
      <div class="calendar-cell time-cell">${slot.label}</div>
    `;

    if (matchingBooking) {
      gridHtml += `
        <div class="calendar-cell" style="grid-column: span 3; padding: 0;">
          <div class="booking-block" style="height: 100%; display: flex; flex-direction: column; justify-content: center; border-radius: 0;">
            <div class="booking-title">${matchingBooking.purpose || 'Reserved Resource'}</div>
            <div class="booking-user">Reserved by: ${matchingBooking.employee_name} (${matchingBooking.start_time} - ${matchingBooking.end_time})</div>
          </div>
        </div>
      `;
    } else {
      gridHtml += `
        <div class="calendar-cell" style="grid-column: span 3; color: var(--text-muted); font-size: 0.85rem; font-style: italic;">
          Time slot is free and available
        </div>
      `;
    }
  });

  container.innerHTML = gridHtml;
}

async function handleBookingSubmit(e) {
  e.preventDefault();

  const form = e.target;
  const resourceName = form.elements['book-resource-name'].value;
  const date = form.elements['book-date'].value;
  const startTime = form.elements['book-start-time'].value;
  const endTime = form.elements['book-end-time'].value;
  const purpose = form.elements['book-purpose'].value;

  if (!startTime || !endTime) {
    showToast('Please specify slot timing range.', 'error');
    return;
  }

  if (endTime <= startTime) {
    showToast('End time must follow start time.', 'error');
    return;
  }

  try {
    await mockService.createBooking({
      employee_id: 4, // Simulated employee ID
      resource_type: resourceName.includes('Room') ? 'Room' : resourceName.includes('Tesla') ? 'Vehicle' : 'Equipment',
      resource_name: resourceName,
      booking_date: date,
      start_time: startTime,
      end_time: endTime,
      purpose: purpose || 'Resource Reservation'
    });

    showToast('Booking reservation completed successfully!');
    closeModal('modal-resource-booking');
    form.reset();

    // Redraw calendar grid
    await renderCalendar();
  } catch (err) {
    showToast(err.message || 'Overlap detected: slot already taken.', 'error');
  }
}
