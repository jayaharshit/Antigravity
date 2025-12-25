/**
 * Bill Splitter - Main Application
 * Manages state and UI interactions for the bill splitting app
 * Updated for Indian billing format with Service Charge, SGST, CGST, Round off
 */

// Application State
const AppState = {
    friends: [],
    items: [],
    assignments: {}, // { itemId: { friendId: quantity } }
    nextFriendId: 1,
    nextItemId: 1
};

// Color palette for friends
const friendColors = [
    'linear-gradient(135deg, #6366f1, #8b5cf6)',
    'linear-gradient(135deg, #ec4899, #f43f5e)',
    'linear-gradient(135deg, #14b8a6, #06b6d4)',
    'linear-gradient(135deg, #f59e0b, #f97316)',
    'linear-gradient(135deg, #10b981, #22c55e)',
    'linear-gradient(135deg, #8b5cf6, #a855f7)',
    'linear-gradient(135deg, #3b82f6, #6366f1)',
    'linear-gradient(135deg, #ef4444, #f97316)'
];

// DOM Elements
const elements = {
    friendInput: null,
    addFriendBtn: null,
    friendsList: null,
    friendsHelper: null,
    itemNameInput: null,
    itemPriceInput: null,
    itemQtyInput: null,
    addItemBtn: null,
    itemsList: null,
    serviceChargeInput: null,
    sgstInput: null,
    cgstInput: null,
    roundOffInput: null,
    discountInput: null,
    netAmount: null,
    assignmentGrid: null,
    summaryGrid: null,
    grandTotal: null,
    exportBtn: null
};

/**
 * Initialize the application
 */
function init() {
    // Cache DOM elements
    elements.friendInput = document.getElementById('friend-input');
    elements.addFriendBtn = document.getElementById('add-friend-btn');
    elements.friendsList = document.getElementById('friends-list');
    elements.friendsHelper = document.getElementById('friends-helper');
    elements.itemNameInput = document.getElementById('item-name-input');
    elements.itemPriceInput = document.getElementById('item-price-input');
    elements.itemQtyInput = document.getElementById('item-qty-input');
    elements.addItemBtn = document.getElementById('add-item-btn');
    elements.itemsList = document.getElementById('items-list');
    elements.serviceChargeInput = document.getElementById('service-charge-input');
    elements.sgstInput = document.getElementById('sgst-input');
    elements.cgstInput = document.getElementById('cgst-input');
    elements.roundOffInput = document.getElementById('roundoff-input');
    elements.discountInput = document.getElementById('discount-input');
    elements.netAmount = document.getElementById('net-amount');
    elements.assignmentGrid = document.getElementById('assignment-grid');
    elements.summaryGrid = document.getElementById('summary-grid');
    elements.grandTotal = document.getElementById('grand-total');
    elements.exportBtn = document.getElementById('export-btn');
    
    // Bind event listeners
    bindEvents();
    
    // Initial render
    renderAll();
}

/**
 * Bind all event listeners
 */
function bindEvents() {
    // Friend management
    elements.addFriendBtn.addEventListener('click', addFriend);
    elements.friendInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') addFriend();
    });
    
    // Item management
    elements.addItemBtn.addEventListener('click', addItem);
    elements.itemNameInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') addItem();
    });
    elements.itemPriceInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') addItem();
    });
    elements.itemQtyInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') addItem();
    });
    
    // Bill extras changes
    elements.serviceChargeInput.addEventListener('input', updateSummary);
    elements.sgstInput.addEventListener('input', updateSummary);
    elements.cgstInput.addEventListener('input', updateSummary);
    elements.roundOffInput.addEventListener('input', updateSummary);
    elements.discountInput.addEventListener('input', updateSummary);
    
    // Export
    elements.exportBtn.addEventListener('click', exportToExcel);
}

/**
 * Get current extras values
 */
function getExtras() {
    return {
        serviceCharge: parseFloat(elements.serviceChargeInput.value) || 0,
        sgst: parseFloat(elements.sgstInput.value) || 0,
        cgst: parseFloat(elements.cgstInput.value) || 0,
        roundOff: parseFloat(elements.roundOffInput.value) || 0,
        discount: parseFloat(elements.discountInput.value) || 0
    };
}

/**
 * Add a new friend
 */
function addFriend() {
    const name = elements.friendInput.value.trim();
    if (!name) return;
    
    // Check for duplicate
    if (AppState.friends.some(f => f.name.toLowerCase() === name.toLowerCase())) {
        alert('This friend is already added!');
        return;
    }
    
    const friend = {
        id: 'friend_' + AppState.nextFriendId++,
        name: name,
        color: friendColors[(AppState.friends.length) % friendColors.length]
    };
    
    AppState.friends.push(friend);
    elements.friendInput.value = '';
    elements.friendInput.focus();
    
    renderFriends();
    renderAssignments();
    updateSummary();
}

/**
 * Remove a friend
 */
function removeFriend(friendId) {
    AppState.friends = AppState.friends.filter(f => f.id !== friendId);
    
    // Remove friend from all assignments
    Object.keys(AppState.assignments).forEach(itemId => {
        delete AppState.assignments[itemId][friendId];
    });
    
    renderFriends();
    renderAssignments();
    updateSummary();
}

/**
 * Render friends list
 */
function renderFriends() {
    if (AppState.friends.length === 0) {
        elements.friendsList.innerHTML = '';
        elements.friendsHelper.style.display = 'block';
        return;
    }
    
    elements.friendsHelper.style.display = 'none';
    elements.friendsList.innerHTML = AppState.friends.map(friend => `
        <div class="friend-tag" style="background: ${friend.color}">
            <span>${friend.name}</span>
            <button class="remove-btn" onclick="removeFriend('${friend.id}')" title="Remove">×</button>
        </div>
    `).join('');
}

/**
 * Add a new item
 */
function addItem() {
    const name = elements.itemNameInput.value.trim();
    const price = parseFloat(elements.itemPriceInput.value);
    const quantity = parseInt(elements.itemQtyInput.value) || 1;
    
    if (!name) {
        alert('Please enter an item name');
        return;
    }
    
    if (isNaN(price) || price <= 0) {
        alert('Please enter a valid price');
        return;
    }
    
    const item = {
        id: 'item_' + AppState.nextItemId++,
        name: name,
        price: price,
        quantity: quantity
    };
    
    AppState.items.push(item);
    AppState.assignments[item.id] = {};
    
    // Clear inputs
    elements.itemNameInput.value = '';
    elements.itemPriceInput.value = '';
    elements.itemQtyInput.value = '1';
    elements.itemNameInput.focus();
    
    renderItems();
    renderAssignments();
    updateSummary();
}

/**
 * Remove an item
 */
function removeItem(itemId) {
    AppState.items = AppState.items.filter(i => i.id !== itemId);
    delete AppState.assignments[itemId];
    
    renderItems();
    renderAssignments();
    updateSummary();
}

/**
 * Edit an item
 */
function editItem(itemId) {
    const item = AppState.items.find(i => i.id === itemId);
    if (!item) return;
    
    // Prompt for new price
    const newPriceStr = prompt(`Edit price for "${item.name}":`, item.price);
    if (newPriceStr === null) return; // Cancelled
    
    const newPrice = parseFloat(newPriceStr);
    if (isNaN(newPrice) || newPrice <= 0) {
        alert('Please enter a valid price');
        return;
    }
    
    // Update the item
    item.price = newPrice;
    
    renderItems();
    renderAssignments();
    updateSummary();
}

/**
 * Render items list
 */
function renderItems() {
    if (AppState.items.length === 0) {
        elements.itemsList.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">🧾</div>
                <p>No items added yet</p>
            </div>
        `;
        return;
    }
    
    elements.itemsList.innerHTML = AppState.items.map(item => `
        <div class="item-row">
            <span class="item-name">${item.name}</span>
            <span class="item-price">${Calculator.formatCurrency(item.price)}</span>
            <span class="item-qty">×${item.quantity}</span>
            <span class="item-total">${Calculator.formatCurrency(item.price * item.quantity)}</span>
            <div class="item-actions">
                <button class="item-edit" onclick="editItem('${item.id}')" title="Edit">✏️</button>
                <button class="item-remove" onclick="removeItem('${item.id}')" title="Remove">×</button>
            </div>
        </div>
    `).join('');
}

/**
 * Render assignment grid
 */
function renderAssignments() {
    if (AppState.items.length === 0 || AppState.friends.length === 0) {
        elements.assignmentGrid.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">👥</div>
                <p>Add friends and items to assign</p>
            </div>
        `;
        return;
    }
    
    elements.assignmentGrid.innerHTML = AppState.items.map(item => `
        <div class="assignment-card">
            <div class="assignment-card-header">
                <div class="assignment-item-info">
                    <span class="assignment-item-name">${item.name}</span>
                    <span class="assignment-item-price">${Calculator.formatCurrency(item.price)}</span>
                </div>
                <span class="assignment-item-qty">Total Qty: ${item.quantity}</span>
            </div>
            <div class="assignment-friends">
                ${AppState.friends.map(friend => {
                    const qty = AppState.assignments[item.id]?.[friend.id] || 0;
                    return `
                        <div class="friend-assignment">
                            <label for="assign_${item.id}_${friend.id}">${friend.name}:</label>
                            <input type="number" 
                                id="assign_${item.id}_${friend.id}"
                                min="0" 
                                max="${item.quantity}"
                                step="any"
                                value="${qty}"
                                onchange="updateAssignment('${item.id}', '${friend.id}', this.value)">
                        </div>
                    `;
                }).join('')}
            </div>
        </div>
    `).join('');
}

/**
 * Update assignment quantity
 */
function updateAssignment(itemId, friendId, value) {
    const qty = parseFloat(value) || 0;
    const item = AppState.items.find(i => i.id === itemId);
    
    if (!item) return;
    
    // Validate quantity doesn't exceed item quantity
    const currentAssignments = AppState.assignments[itemId] || {};
    const otherAssigned = Object.entries(currentAssignments)
        .filter(([fId]) => fId !== friendId)
        .reduce((sum, [, q]) => sum + q, 0);
    
    const maxAllowed = item.quantity - otherAssigned;
    const finalQty = Math.min(Math.max(0, qty), maxAllowed);
    
    if (!AppState.assignments[itemId]) {
        AppState.assignments[itemId] = {};
    }
    AppState.assignments[itemId][friendId] = finalQty;
    
    // Update input if value was clamped
    if (finalQty !== qty) {
        document.getElementById(`assign_${itemId}_${friendId}`).value = finalQty;
    }
    
    updateSummary();
}

/**
 * Update the summary section
 */
function updateSummary() {
    const extras = getExtras();
    
    // Update net amount display
    const netAmount = Calculator.calculateNetAmount(AppState.items, extras);
    elements.netAmount.textContent = Calculator.formatCurrency(netAmount);
    
    const shares = Calculator.calculateShares(
        AppState.friends,
        AppState.items,
        AppState.assignments,
        extras
    );
    
    renderSummary(shares);
    
    const grandTotal = Calculator.calculateGrandTotal(shares);
    elements.grandTotal.textContent = Calculator.formatCurrency(grandTotal);
}

/**
 * Render summary cards
 */
function renderSummary(shares) {
    if (AppState.friends.length === 0) {
        elements.summaryGrid.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📊</div>
                <p>Add friends to see the split</p>
            </div>
        `;
        return;
    }
    
    elements.summaryGrid.innerHTML = AppState.friends.map(friend => {
        const share = shares[friend.id];
        const initial = friend.name.charAt(0).toUpperCase();
        
        return `
            <div class="summary-card">
                <div class="summary-card-header">
                    <div class="friend-avatar" style="background: ${friend.color}">${initial}</div>
                    <span class="friend-summary-name">${friend.name}</span>
                </div>
                <div class="summary-items">
                    ${share.items.length > 0 ? share.items.map(item => `
                        <div class="summary-item">
                            <span>${item.name} ×${item.quantity}</span>
                            <span>${Calculator.formatCurrency(item.price)}</span>
                        </div>
                    `).join('') : '<div class="summary-item"><span>No items assigned</span></div>'}
                </div>
                <div class="summary-breakdown">
                    <div class="breakdown-row">
                        <span>Subtotal</span>
                        <span>${Calculator.formatCurrency(share.subtotal)}</span>
                    </div>
                    ${share.serviceCharge > 0 ? `
                        <div class="breakdown-row">
                            <span>Service Charge</span>
                            <span>${Calculator.formatCurrency(share.serviceCharge)}</span>
                        </div>
                    ` : ''}
                    ${share.sgst > 0 ? `
                        <div class="breakdown-row">
                            <span>SGST</span>
                            <span>${Calculator.formatCurrency(share.sgst)}</span>
                        </div>
                    ` : ''}
                    ${share.cgst > 0 ? `
                        <div class="breakdown-row">
                            <span>CGST</span>
                            <span>${Calculator.formatCurrency(share.cgst)}</span>
                        </div>
                    ` : ''}
                    ${share.roundOff !== 0 ? `
                        <div class="breakdown-row">
                            <span>Round Off</span>
                            <span>${Calculator.formatCurrency(share.roundOff)}</span>
                        </div>
                    ` : ''}
                    ${share.discount > 0 ? `
                        <div class="breakdown-row discount-row">
                            <span>Discount</span>
                            <span>-${Calculator.formatCurrency(share.discount)}</span>
                        </div>
                    ` : ''}
                    <div class="breakdown-row total">
                        <span>Total</span>
                        <span>${Calculator.formatCurrency(share.total)}</span>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

/**
 * Export to Excel
 */
function exportToExcel() {
    if (AppState.friends.length === 0) {
        alert('Please add at least one friend before exporting.');
        return;
    }
    
    if (AppState.items.length === 0) {
        alert('Please add at least one item before exporting.');
        return;
    }
    
    const extras = getExtras();
    
    const shares = Calculator.calculateShares(
        AppState.friends,
        AppState.items,
        AppState.assignments,
        extras
    );
    
    ExcelExport.exportToExcel(
        AppState.friends,
        AppState.items,
        shares,
        extras
    );
}

/**
 * Render all components
 */
function renderAll() {
    renderFriends();
    renderItems();
    renderAssignments();
    updateSummary();
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', init);
