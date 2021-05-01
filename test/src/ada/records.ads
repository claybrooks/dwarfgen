package Records is

    type Record_A is record
        a: Character;
        b: Integer;
    end record;

    type Record_B is record
        a: String(1..100);
    end record;

    type Record_C is record
        a: String(0..100);
    end record;

    type Record_D is record
        a: String(10..100);
    end record;

    --type Record_C is record
    --    a : Character;
    --    b : Integer;
    --end record;

    --for Record_C use record
    --    a at 0 range 0 .. 3;
    --    b at 0 range 4 .. 7;
    --end record;

    a : Record_A;
    b : Record_B;
    c : Record_C;
    d : Record_D;

end Records;