package Records is

    type RecordA is record
        a: Character;
        b: Integer;
    end record;

    type RecordB is record
        a: String(1..100);
    end record;

    type RecordC is record
        a: String(0..100);
    end record;

    type RecordD is record
        a: String(10..100);
    end record;

    type RecordE is record
        a: String(10..100);
    end record;

    type RecordF is record
        a : Boolean;
        b : Integer range 1 .. 120;
    end record;

    for RecordF use record
        a at 0 range 0 .. 0;
        b at 0 range 1 .. 7;
    end record;

    a : RecordA;
    b : RecordB;
    c : RecordC;
    d : RecordD;
    e : RecordE;
    f : RecordF;

end Records;