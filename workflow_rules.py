ALLOWED = {
 'placed': {'paid','cancelled'}, 'paid': {'assigned','waiting_locker','cancelled'},
 'assigned': {'picked_up','paid'}, 'picked_up': {'at_hub'}, 'at_hub': {'deposited'},
 'deposited': {'collected','expired_review'}, 'expired_review': {'returned_to_seller','deposited'},
 'collected': {'return_requested'}, 'return_requested': {'return_approved','collected'},
 'return_approved': {'return_received'}, 'return_received': {'refunded'},
}
