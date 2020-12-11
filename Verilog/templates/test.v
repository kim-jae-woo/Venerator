
//==========================================
// templates
//==========================================

    assign apb_wr = psel & ~penable & pwrite;
    assign apb_rd = psel & ~penable & ~pwrite;

