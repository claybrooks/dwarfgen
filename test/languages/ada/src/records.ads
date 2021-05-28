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

    type BaseRecord is tagged record
        a: Character;
        b: Integer;
    end record;

    type DerivedRecord is new BaseRecord with record
        c: Integer;
        d: Integer;
    end record;

    type NonTaggedBaseRecord is record
        a: Integer;
        b: Integer;
    end record;

    type VariantSelect is (One, Two, Three);

    -- The_Type is called the discriminant of the type
    type VariantRecord(Selector: VariantSelect := One) is record

        common: Integer;

        case Selector is
            when One =>
                a: boolean;
            when Two =>
                b: Positive;
            when Three =>
                c: String(1..5);
        end case;
    end record;

    type NonTaggedDerivedRecord is new NonTaggedBaseRecord;

    a : RecordA;
    b : RecordB;
    c : RecordC;
    d : RecordD;
    e : RecordE;
    f : RecordF;

    --g: BaseRecord;
    h: DerivedRecord;

    i: NonTaggedDerivedRecord;

    --variant: VariantRecord;
end Records;