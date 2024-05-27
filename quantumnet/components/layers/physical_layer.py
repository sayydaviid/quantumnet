from ...objects import Logger, Qubit, Epr
from ...components import Host #, Network
from random import uniform

class PhysicalLayer():
    def __init__(self, network, physical_layer_id: int = 0):
        """
        Inicializa a camada física.
        
        args:
            physical_layer_id : int : Id da camada física.
        """

        self._physical_layer_id = physical_layer_id
        self._network = network
        self._qubits = []
        self._initial_qubits_fidelity = 1.0
        self._count_qubit = 0
        self.logger = Logger.get_instance()
        
    def __str__(self):
        """ Retorna a representação em string da camada física. 
        
        returns:
            str : Representação em string da camada física."""
        return f'Physical Layer {self.physical_layer_id}'
      
    @property
    def physical_layer_id(self):
        """
        Retorna o id da camada física.
        
        returns:
            int : Id da camada física.
        """
        return self._physical_layer_id
    
    @property
    def qubits(self):
        """
        Retorna os qubits da camada física.
        
        returns:
            list : Lista de qubits da camada física.
        """
        return self._qubits

    def create_qubit(self, host_id: int):
        """
        Cria um qubit e adiciona à memória do host especificado.

        Args:
            host_id (int): ID do host onde o qubit será criado.

        Raises:
            Exception: Se o host especificado não existir na rede.
        """
        if host_id not in self._network.hosts:
            raise Exception(f'Host {host_id} não existe na rede.')
        
        # Cria o qubit e adiciona à memória do host
        qubit_id = self._count_qubit
        qubit = Qubit(qubit_id, self._initial_qubits_fidelity)
        self._network.hosts[host_id].add_qubit(qubit)
        self._count_qubit += 1
        self.logger.debug(f'Qubit {qubit_id} criado com fidelidade inicial {self._initial_qubits_fidelity} e adicionado à memória do Host {host_id}.')
    
    def entangle(self, qubits: list):
        # TODO: Possível função genérica para entrelaçar inúmeros qubits. GHZ, W, etc.
        """
        Entrelaça n qubits.
        
        args:
            qubits: list : Lista de qubits a serem entrelaçados.
        """
        pass
    
    def create_epr_pair(self, qubit1: Qubit, qubit2: Qubit):
        """
        Cria um par de qubits entrelaçados.
        
        returns:
            Qubit, Qubit : Par de qubits entrelaçados.
        """
        fidelidade_qubit1 = self.fidelity_measurement_only_one(qubit1)
        fidelidade_qubit2 = self.fidelity_measurement_only_one(qubit2)
        fidelidade_inicial_epr = fidelidade_qubit1 * fidelidade_qubit2
        epr = Epr([qubit1, qubit2], fidelidade_inicial_epr)
        
        return epr
      
    def fidelity_measurement_only_one(self, qubit: Qubit):
        """
        Mede a fidelidade de um qubit.

        Args:
            qubit (Qubit): Qubit.

        Returns:
            float: Fidelidade do qubit.
        """
        fidelity = qubit.get_current_fidelity()
        self.logger.log(f'A fidelidade do qubit {qubit} é {fidelity}')
        return fidelity
    
    def fidelity_measurement(self, qubit1: Qubit, qubit2: Qubit):
        """
        Mede a fidelidade entre dois qubits.

        Args:
            qubit1 (Qubit): Qubit 1.
            qubit2 (Qubit): Qubit 2.

        Returns:
            float: Fidelidade entre os qubits.
        """
        fidelity = qubit1.get_current_fidelity() * qubit2.get_current_fidelity()
        self.logger.log(f'A fidelidade entre o qubit {qubit1} e o qubit {qubit2} é {fidelity}')
        return fidelity
    
    def entanglement_creation_heralding_protocol(self, alice: Host, bob: Host):

        """ 
        Protocolo de criação de emaranhamento com sinalização.
        
        returns:
            bool : True se o protocolo foi bem sucedido, False caso contrário.
        """
        # Alice e Bob criam um par EPR
        qubit1 = alice.get_last_qubit()
        qubit2 = bob.get_last_qubit()
        self.create_epr_pair(qubit1, qubit2)
        # Checa a fidelidade
        fidelity = self.fidelity_measurement(qubit1, qubit2)
        
        # Adicionar par EPR no canal
        
        # Pode dar errado tanto pela probabilidade, quanto pela fidelidade
        if fidelity > 0.9:
            self.logger.log('O protocolo de criação de emaranhamento foi bem sucedido.')
            # Adicionar par EPR no canal
            return True
        self.logger.log('O protocolo de criação de emaranhamento falhou.')
        return False
    
    def echp_on_replay(self, alice_host_id: int, bob_host_id: int):
        # TODO: Fazer a docsctring
        # TODO: Adicionar log de sucesso ou falha
        
        # Obtendo os qubits de Alice e Bob
        qubit1 = self._network.hosts[alice_host_id].get_last_qubit()
        qubit2 = self._network.hosts[bob_host_id].get_last_qubit()
        
        # Acessando a fidelidade dos qubits
        fidelidade_qubit1 = self.fidelity_measurement_only_one(qubit1)
        fidelidade_qubit2 = self.fidelity_measurement_only_one(qubit2)
               
        # Proabilidade de Sucesso do ECHP: Prob_replay_epr_create * Fidelidade_qubit1* Fidelidade_qubit2
        prob_replay_epr_create = self._network.edges[alice_host_id, bob_host_id]['prob_replay_epr_create']
        proabilidade_de_sucesso_do_echp = prob_replay_epr_create * fidelidade_qubit1 * fidelidade_qubit2
        
        if uniform(0, 1) < proabilidade_de_sucesso_do_echp:
            epr = self.create_epr_pair(qubit1, qubit2)
            self._network.edges[alice_host_id, bob_host_id]['eprs'].append(epr)
            self.logger.log(f'A probabilidade de sucesso do ECHP é {proabilidade_de_sucesso_do_echp}')
            return True
        
        return False

    def echp_on_replay(self, alice: Host, bob: Host):
        #o ECHP_on_replay é quando a fidelidade decaiu e o protocolo é refeito
        pass