/**
 * Excel Export Module
 * Handles exporting bill split data to Excel using SheetJS
 * Updated for Indian billing format
 */

const ExcelExport = {
    /**
     * Export the bill split data to an Excel file
     * @param {Array} friends - Array of friend objects
     * @param {Array} items - Array of item objects
     * @param {Object} shares - Calculated shares for each friend
     * @param {Object} extras - Object with serviceCharge, sgst, cgst, roundOff
     */
    exportToExcel(friends, items, shares, extras) {
        const { serviceCharge = 0, sgst = 0, cgst = 0, roundOff = 0 } = extras;
        
        // Create workbook
        const wb = XLSX.utils.book_new();
        
        // Sheet 1: Summary
        const summaryData = this.createSummarySheet(friends, shares, extras);
        const summaryWS = XLSX.utils.aoa_to_sheet(summaryData);
        this.styleSheet(summaryWS, summaryData);
        XLSX.utils.book_append_sheet(wb, summaryWS, 'Summary');
        
        // Sheet 2: Item Details (like manual spreadsheet)
        const detailsData = this.createDetailsSheet(friends, items, shares, extras);
        const detailsWS = XLSX.utils.aoa_to_sheet(detailsData);
        this.styleSheet(detailsWS, detailsData);
        XLSX.utils.book_append_sheet(wb, detailsWS, 'Item Details');
        
        // Generate filename with date
        const date = new Date();
        const dateStr = date.toISOString().slice(0, 10);
        const filename = `Bill_Split_${dateStr}.xlsx`;
        
        // Download the file
        XLSX.writeFile(wb, filename);
    },
    
    /**
     * Create the summary sheet data
     */
    createSummarySheet(friends, shares, extras) {
        const { serviceCharge = 0, sgst = 0, cgst = 0, roundOff = 0 } = extras;
        const data = [];
        
        // Title
        data.push(['BILL SPLIT SUMMARY']);
        data.push(['Generated on: ' + new Date().toLocaleString()]);
        data.push([]);
        
        // Bill Extras Summary
        data.push(['BILL EXTRAS']);
        data.push(['Service Charge:', '₹' + serviceCharge.toFixed(2)]);
        data.push(['State GST (SGST):', '₹' + sgst.toFixed(2)]);
        data.push(['Central GST (CGST):', '₹' + cgst.toFixed(2)]);
        data.push(['Round Off:', '₹' + roundOff.toFixed(2)]);
        data.push([]);
        
        // Headers
        data.push(['Friend', 'Items', 'Subtotal', 'Service Charge', 'SGST', 'CGST', 'Round Off', 'Total']);
        
        // Data rows
        let grandTotal = 0;
        friends.forEach(friend => {
            const share = shares[friend.id];
            if (share) {
                const itemsList = share.items.map(i => `${i.name} (${i.quantity})`).join(', ') || 'No items';
                data.push([
                    friend.name,
                    itemsList,
                    '₹' + share.subtotal.toFixed(2),
                    '₹' + share.serviceCharge.toFixed(2),
                    '₹' + share.sgst.toFixed(2),
                    '₹' + share.cgst.toFixed(2),
                    '₹' + share.roundOff.toFixed(2),
                    '₹' + share.total.toFixed(2)
                ]);
                grandTotal += share.total;
            }
        });
        
        // Grand total
        data.push([]);
        data.push(['', '', '', '', '', '', 'NET AMOUNT:', '₹' + grandTotal.toFixed(2)]);
        
        return data;
    },
    
    /**
     * Create the item details sheet data with full breakdown like manual spreadsheet
     */
    createDetailsSheet(friends, items, shares, extras) {
        const { serviceCharge = 0, sgst = 0, cgst = 0, roundOff = 0, discount = 0 } = extras;
        const data = [];
        
        // Create header with friend names
        const header = ['Item', 'Price', 'Qty'];
        friends.forEach(friend => {
            header.push(friend.name);
        });
        header.push('Total');
        data.push(header);
        
        // Data rows for each item - showing AMOUNTS not quantities
        let itemRowTotal = 0;
        items.forEach(item => {
            const row = [item.name, item.price, item.quantity];
            let rowSum = 0;
            friends.forEach(friend => {
                const share = shares[friend.id];
                if (share) {
                    const itemShare = share.items.find(i => i.name === item.name);
                    const amount = itemShare ? itemShare.price : 0;
                    row.push(amount);
                    rowSum += amount;
                } else {
                    row.push(0);
                }
            });
            row.push(rowSum);
            itemRowTotal += rowSum;
            data.push(row);
        });
        
        // Subtotals row (blank item name, shows person totals)
        const subtotalRow = ['', '', ''];
        let subTotal = 0;
        friends.forEach(friend => {
            const share = shares[friend.id];
            const amount = share ? share.subtotal : 0;
            subtotalRow.push(amount);
            subTotal += amount;
        });
        subtotalRow.push(subTotal);
        data.push(subtotalRow);
        
        // Service Charge row
        const serviceChargeRow = ['Service Charge', serviceCharge, ''];
        let scTotal = 0;
        friends.forEach(friend => {
            const share = shares[friend.id];
            const amount = share ? share.serviceCharge : 0;
            serviceChargeRow.push(amount);
            scTotal += amount;
        });
        serviceChargeRow.push(scTotal);
        data.push(serviceChargeRow);
        
        // GST row (combined SGST + CGST)
        const totalGst = sgst + cgst;
        const gstRow = ['GST', totalGst, ''];
        let gstTotal = 0;
        friends.forEach(friend => {
            const share = shares[friend.id];
            const amount = share ? (share.sgst + share.cgst) : 0;
            gstRow.push(amount);
            gstTotal += amount;
        });
        gstRow.push(gstTotal);
        data.push(gstRow);
        
        // Total to Pay row (before discount)
        const totalToPayRow = ['Total to Pay', '', ''];
        let totalToPay = 0;
        friends.forEach(friend => {
            const share = shares[friend.id];
            const amount = share ? (share.subtotal + share.serviceCharge + share.sgst + share.cgst + share.roundOff) : 0;
            totalToPayRow.push(amount);
            totalToPay += amount;
        });
        totalToPayRow.push(totalToPay);
        data.push(totalToPayRow);
        
        // Discount row
        const discountRow = ['Discount', -discount, ''];
        let discountTotal = 0;
        friends.forEach(friend => {
            const share = shares[friend.id];
            const amount = share && share.discount ? -share.discount : 0;
            discountRow.push(amount);
            discountTotal += amount;
        });
        discountRow.push(discountTotal);
        data.push(discountRow);
        
        // Final Amount row
        const finalRow = ['', '', ''];
        let grandTotal = 0;
        friends.forEach(friend => {
            const share = shares[friend.id];
            const amount = share ? share.total : 0;
            finalRow.push(amount);
            grandTotal += amount;
        });
        finalRow.push(grandTotal);
        data.push(finalRow);
        
        return data;
    },
    
    /**
     * Apply basic styling to the sheet
     */
    styleSheet(ws, data) {
        // Set column widths
        const colWidths = [];
        data.forEach(row => {
            row.forEach((cell, idx) => {
                const cellWidth = cell ? cell.toString().length : 10;
                colWidths[idx] = Math.max(colWidths[idx] || 10, cellWidth + 2);
            });
        });
        
        ws['!cols'] = colWidths.map(w => ({ wch: Math.min(w, 50) }));
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ExcelExport;
}
