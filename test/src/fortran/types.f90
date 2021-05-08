program prog

    type ItemA
        CHARACTER :: a
        INTEGER :: b
    end type ItemA

    type ItemB
        INTEGER :: a
        INTEGER :: b
    end type ItemB

    type(ItemA) item_a
    type(ItemB) item_b

    item_a%a = '1'
    item_b%a = 0

end program prog
