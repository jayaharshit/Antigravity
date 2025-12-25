/**
 * Bill Splitting Calculator Module
 * Handles all cost calculations for splitting bills among friends
 * Updated for Indian billing format with Service Charge, SGST, CGST, Round off
 */

const Calculator = {
    /**
     * Calculate the share for each friend based on item assignments
     * @param {Array} friends - Array of friend objects {id, name}
     * @param {Array} items - Array of item objects {id, name, price, quantity}
     * @param {Object} assignments - Object mapping itemId to {friendId: quantity}
     * @param {Object} extras - Object with serviceCharge, sgst, cgst, roundOff
     * @returns {Object} - Calculated shares for each friend
     */
    calculateShares(friends, items, assignments, extras = {}) {
        const { serviceCharge = 0, sgst = 0, cgst = 0, roundOff = 0, discount = 0 } = extras;
        const result = {};
        
        // Initialize result for each friend
        friends.forEach(friend => {
            result[friend.id] = {
                name: friend.name,
                items: [],
                subtotal: 0,
                serviceCharge: 0,
                sgst: 0,
                cgst: 0,
                roundOff: 0,
                discount: 0,
                total: 0
            };
        });
        
        // Calculate subtotal from items
        let billSubtotal = 0;
        
        items.forEach(item => {
            const itemAssignments = assignments[item.id] || {};
            const totalAssignedQty = Object.values(itemAssignments).reduce((sum, qty) => sum + qty, 0);
            
            if (totalAssignedQty === 0) return;
            
            // item.price is already the unit price (entered by user)
            const pricePerUnit = item.price;
            
            Object.entries(itemAssignments).forEach(([friendId, qty]) => {
                if (qty > 0 && result[friendId]) {
                    const itemCost = pricePerUnit * qty;
                    result[friendId].items.push({
                        name: item.name,
                        quantity: qty,
                        price: itemCost
                    });
                    result[friendId].subtotal += itemCost;
                    billSubtotal += itemCost;
                }
            });
        });
        
        // Calculate extras proportionally based on each friend's subtotal
        // Discount is split equally among friends who have items
        const friendsWithItems = Object.values(result).filter(share => share.subtotal > 0).length;
        const discountPerFriend = friendsWithItems > 0 ? discount / friendsWithItems : 0;
        
        Object.keys(result).forEach(friendId => {
            const share = result[friendId];
            if (share.subtotal > 0 && billSubtotal > 0) {
                const proportion = share.subtotal / billSubtotal;
                share.serviceCharge = serviceCharge * proportion;
                share.sgst = sgst * proportion;
                share.cgst = cgst * proportion;
                share.roundOff = roundOff * proportion;
                share.discount = discountPerFriend;
                share.total = share.subtotal + share.serviceCharge + share.sgst + share.cgst + share.roundOff - share.discount;
            }
        });
        
        return result;
    },
    
    /**
     * Calculate the net amount (subtotal + all extras)
     * @param {Array} items - Array of items
     * @param {Object} extras - Object with serviceCharge, sgst, cgst, roundOff
     * @returns {number} - Net amount
     */
    calculateNetAmount(items, extras = {}) {
        const { serviceCharge = 0, sgst = 0, cgst = 0, roundOff = 0, discount = 0 } = extras;
        
        const subtotal = items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        return subtotal + serviceCharge + sgst + cgst + roundOff - discount;
    },
    
    /**
     * Calculate the grand total of all shares
     * @param {Object} shares - Object containing each friend's share
     * @returns {number} - Grand total
     */
    calculateGrandTotal(shares) {
        return Object.values(shares).reduce((sum, share) => sum + share.total, 0);
    },
    
    /**
     * Format currency value
     * @param {number} value - The value to format
     * @returns {string} - Formatted currency string
     */
    formatCurrency(value) {
        return '₹' + value.toFixed(2);
    },
    
    /**
     * Validate that all items are assigned
     * @param {Array} items - Array of items
     * @param {Object} assignments - Assignment object
     * @returns {Object} - Validation result with status and message
     */
    validateAssignments(items, assignments) {
        const unassigned = [];
        
        items.forEach(item => {
            const itemAssignments = assignments[item.id] || {};
            const totalAssignedQty = Object.values(itemAssignments).reduce((sum, qty) => sum + qty, 0);
            
            if (totalAssignedQty === 0) {
                unassigned.push(item.name);
            }
        });
        
        return {
            valid: unassigned.length === 0,
            unassignedItems: unassigned,
            message: unassigned.length > 0 
                ? `The following items are not assigned: ${unassigned.join(', ')}`
                : 'All items are assigned'
        };
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Calculator;
}
