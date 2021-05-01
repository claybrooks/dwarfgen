package Records is

    type Record_A is record
        a: Character;
        b: Integer;
    end record;

    type Record_B is record
        a: String(0..99);
    end record;

    a : Record_A;
    b : Record_B;

end Records;