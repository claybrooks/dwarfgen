program prog

    type ItemA
        CHARACTER :: a
        INTEGER :: b
    end type ItemA

    type(ItemA) item_a
    item_a%a = '1'

end program prog
