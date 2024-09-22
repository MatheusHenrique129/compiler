// Comentário 
{ Comentario }
program ex01;
(* Comentário de bloco *)
var a, b, c: integer;
(* Comentário de bloco *)
begin
(* Comentário de bloco *)
   a := 10;
   (* Comentário de bloco *)
   b := 20;
   (* Comentário de bloco *)
   c := 30;
   (* Comentário de bloco *)
   write(a / b);
   (* Comentário de bloco *)
   write(a + c);
   (* Comentário de bloco *)
   write(a);
   (* Comentário de bloco *)
   write((a + 3) * 4);
   (* Comentário de bloco *)
   if a > 10 then
   { Comentário }
   (* Comentário de bloco *)
   begin
      write(a+10);
      (* Comentário de bloco *)
      a := a + 1
      (* Comentário de bloco *)
   end
   (* Comentário de bloco *)
   else
   (* Comentário de bloco *)
   begin
   (* Comentário de bloco *)
      write(b+20);
      (* Comentário de bloco *)
      b := b + 1
      (* Comentário de bloco *)
   end
   (* Comentário de bloco *)
end.
(* Comentário de bloco *)