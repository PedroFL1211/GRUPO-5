from hashlib import sha256
from django import forms
from .models import Denuncia, Usuario
from .recomendacoes import separar_habilidades


class DenunciaForm(forms.ModelForm):
    destino = forms.ChoiceField(label='Usuário ou habilidade denunciado')

    class Meta:
        model = Denuncia
        fields = ['destino', 'motivo', 'descricao']
        labels = {'motivo': 'Motivo principal', 'descricao': 'Descreva o que aconteceu'}
        widgets = {'descricao': forms.Textarea(attrs={'rows': 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.alvos = {}
        escolhas = [('', 'Selecione o usuário ou a habilidade')]
        for usuario in Usuario.objects.order_by('nome', 'pk'):
            chave = f'u:{usuario.pk}'
            self.alvos[chave] = (usuario, '')
            escolhas.append((chave, f'Usuário: {usuario.nome} (@{usuario.user.username})'))
            for habilidade in separar_habilidades(usuario.habilidadeEnsina).values():
                chave = f'h:{usuario.pk}:{sha256(habilidade.encode()).hexdigest()}'
                self.alvos[chave] = (usuario, habilidade)
                escolhas.append((chave, f'Habilidade: {habilidade} — @{usuario.user.username}'))
        self.fields['destino'].choices = escolhas

    def save(self, commit=True):
        denuncia = super().save(commit=False)
        usuario, habilidade = self.alvos[self.cleaned_data['destino']]
        denuncia.usuario_alvo = usuario
        denuncia.habilidade_alvo = habilidade
        denuncia.tipo = 'habilidade' if habilidade else 'usuario'
        denuncia.alvo = (f'{habilidade} (@{usuario.user.username})' if habilidade else f'@{usuario.user.username}')[:100]
        if commit:
            denuncia.save()
        return denuncia
