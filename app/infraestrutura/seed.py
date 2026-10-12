from sqlalchemy import func, select
from app.domain.models import CardapioItem, Estoque, Produto, Unidade, Usuario
from app.infraestrutura.database import Base, SessionLocal, engine
from app.infraestrutura.security import hash_senha


def popular():
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if db.scalar(select(func.count()).select_from(Unidade)):
            print("O banco já tem dados. Não há nada a ser feito.")
            return
        unidades = [Unidade(nome="Raízes Recife (Matriz)", cidade="Recife", uf="PE"),
                    Unidade(nome="Raízes Salvador", cidade="Salvador", uf="BA")]
        produtos = [Produto(nome="Cuscuz Recheado", categoria="PRATO", preco_base_centavos=1890),
                    Produto(nome="Tapioca de Queijo", categoria="PRATO", preco_base_centavos=1250),
                    Produto(nome="Suco de Cajá", categoria="BEBIDA", preco_base_centavos=950)]
        db.add_all(unidades + produtos)
        db.flush()

        for u in unidades:
            for p in produtos:
                db.add(CardapioItem(unidade_id=u.id, produto_id=p.id, preco_centavos=p.preco_base_centavos))
                db.add(Estoque(unidade_id=u.id, produto_id=p.id, quantidade=50))


        equipe = [

            ('Admnistrador', 'admin@raizes.com', 'Admin@123', 'ADMIN'),
            ('Gerente DEMO', 'gerente@raizes.com', 'Gerente@123', 'GERENTE'),
            ('Atendente DEMO', 'atendente@raizes.com', 'Atendente@123', 'ATENDENTE'),
            ('Cozinha DEMO', 'cozinha@raizes.com', 'Cozinha@123', 'COZINHA'),
            ('Cliente DEMO', 'cliente@raizes.com', 'Cliente@123', 'CLIENTE'),
 ]
        for nome, email, senha, perfil in equipe:
            db.add(Usuario(nome=nome, email=email, senha_hash=hash_senha(senha), perfil=perfil))  
        
        db.commit()
        print("Banco populado com sucesso!")


if __name__=="__main__":
    popular()
    
                    