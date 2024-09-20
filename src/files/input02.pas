program ex01;
var a, b, c: integer;
begin
   a := 10;
   b := 20;
   c := 30;
   write(a / b);
   write(a + c);
   write(a);
   write((a + 3) * 4);
   if a > 10 then
   begin
      write(a+10);
      a := a + 1
   end
   else
   begin
      write(b+20);
      b := b + 1
   end
end.