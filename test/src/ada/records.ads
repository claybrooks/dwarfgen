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

    --type RecordC is record
    --    a : Character;
    --    b : Integer;
    --end record;

    --for RecordC use record
    --    a at 0 range 0 .. 3;
    --    b at 0 range 4 .. 7;
    --end record;

    a : RecordA;
    b : RecordB;
    c : RecordC;
    d : RecordD;
    e : RecordE;
end Records;